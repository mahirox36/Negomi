import re
from fastapi import HTTPException, Request
from typing import TYPE_CHECKING, Optional
import asyncio

from nexon import ComparisonType, Rarity, RequirementType
from nexon.ext.commands import Bot
import nexon
from .auth import check_owner
from modules.Nexon import download_image_to_bytes
from .baseModels import *
from nexon.badge import BadgeManager
import logging

if TYPE_CHECKING:
    from backend.apiManager import APIServer


async def getGuild(client: Bot, id: Optional[int]):
    guild = client.get_guild(1262297191884521514) if not id else client.get_guild(id)
    if not guild:
        guild = (
            await client.fetch_guild(1262297191884521514)
            if not id
            else await client.fetch_guild(id)
        )
    return guild


async def check_guild(guild_id: int):
    badges = await BadgeManager(guild_id).get_all_badges() or []
    if len(badges) >= 8:
        raise HTTPException(
            status_code=403,
            detail="You have exceeded the maximum badge limit for the Free Tier.",
        )


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


async def createBadge(
    request: Request, badge_request: CreateBadgeRequest, guild_id: Optional[int] = None
) -> Dict[str, bool]:
    """Create a new badge"""
    backend: APIServer = request.app.state.backend
    try:
        # Check permissions and badge limits
        if guild_id:
            await check_guild(guild_id)
        elif request:
            await check_owner(request)

        # Convert dictionary requirements to BadgeRequirement objects
        requirements: list[tuple[RequirementType, ComparisonType, str]] = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value")).lower(),
            )
            for req in badge_request.requirements
        ]

        # Get the guild
        guild = await getGuild(backend.client, guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        # Download and process the image with retry mechanism
        max_retries = 3
        image = None

        for attempt in range(max_retries):
            image = await download_image_to_bytes(badge_request.icon_url)
            if image:
                break

            # Wait briefly before retrying
            await asyncio.sleep(0.5)

        # If still no image after retries
        if not image:
            raise HTTPException(
                status_code=400,
                detail="Failed to download or process the image. Please try a different image URL.",
            )

        # Create a safe name for the emoji
        sanitized_name = re.sub(
            r"[^a-zA-Z0-9_]", "", badge_request.name.replace(" ", "_")
        )
        if len(sanitized_name) > 32:  # Discord has a 32 character limit for emoji names
            sanitized_name = sanitized_name[:32]

        # Ensure name isn't empty after sanitization
        if not sanitized_name:
            sanitized_name = "badge"
        if len(f"{sanitized_name}_badge") > 32:
            sanitized_name = f"{sanitized_name[:32 - 6]}_badge"
        else:
            sanitized_name = f"{sanitized_name}_badge"
        

        # Try to create emoji with error handling
        try:
            emoji = await guild.create_custom_emoji(
                name=sanitized_name,
                image=image,
                reason=f"Creating New Badge Called {badge_request.name}",
            )
        except HTTPException as emoji_error:
            # Handle Discord API errors specifically
            if "maximum number of emojis" in str(emoji_error).lower():
                raise HTTPException(
                    status_code=400,
                    detail="This server has reached the maximum number of custom emojis.",
                )
            elif "asset exceeds maximum size" in str(emoji_error).lower():
                raise HTTPException(
                    status_code=400,
                    detail="Image file size is too large. Please use a smaller image.",
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to create emoji: {str(emoji_error)}",
                )

        # Create the badge in the database
        await BadgeManager(guild_id).create_badge(
            name=badge_request.name,
            description=badge_request.description,
            icon_url=badge_request.icon_url,
            emoji=f"<:{emoji.name}:{emoji.id}>",
            rarity=Rarity(badge_request.rarity),
            requirements=requirements,
            hidden=badge_request.hidden,
        )

        return {"success": True}
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code, detail=http_error.detail
        )
    except nexon.errors.Forbidden as forbidden_error:
        # Handle permission errors
        logger.error(f"Permission error: {forbidden_error}")
        raise HTTPException(
            status_code=403,
            detail="The bot doesn't have permission to create emojis in this server.",
        )
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error in createBadge: {str(e)}", exc_info=True)

        # Raise a more detailed error response
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


async def getBadges(request: Request, guild_id: Optional[int] = None):
    """Get all badges"""
    try:

        if not guild_id:
            await check_owner(request)

        badge_manager = BadgeManager(guild_id)
        badges = await badge_manager.get_all_badges()
        # Convert badges to a list of dictionaries, handling each badge individually
        badge_list: List[Dict[str, str | int | bool | List[Dict[str, str]]]] = []
        for badge in badges:
            try:
                badge_dict = await badge.to_dict()
                badge_list.append(badge_dict)
            except Exception as e:
                continue
        return {"badges": badge_list}
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code, detail=http_error.detail
        )

    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, guild_id: {guild_id}")

        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}",
        )


async def editBadge(
    badge_id: int,
    request: Request,
    request_badge: CreateBadgeRequest,
    guild_id: Optional[int] = None,
) -> Dict[str, bool]:
    """Edit an existing badge"""
    try:
        backend: APIServer = request.app.state.backend
        if not guild_id:
            await check_owner(request)

        badge_manager = BadgeManager(guild_id)

        # Convert requirements
        requirements = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value")).lower(),
            )
            for req in request_badge.requirements
        ]

        # Handle emoji update if icon changed
        existing_badge = await badge_manager.get_badge(badge_id)
        if not existing_badge:
            raise HTTPException(status_code=404, detail="Badge not found")

        emoji_str = existing_badge.emoji
        if existing_badge.icon_url != request_badge.icon_url:
            guild = await getGuild(backend.client, guild_id)

            # Delete old image and emoji
            await backend.storage.delete_file(existing_badge.icon_url.split("/")[-1])
            emoji_id = re.search(r"<:\w+:(\d+)>", existing_badge.emoji)
            if emoji_id:
                emoji_id = int(emoji_id.group(1))
                emoji = nexon.utils.get(guild.emojis, id=emoji_id)
                if emoji:
                    await emoji.delete()

            # Create new emoji
            image = await download_image_to_bytes(request_badge.icon_url)
            if not image:
                raise Exception("No image found")
            new_emoji = await guild.create_custom_emoji(
                name=f"{request_badge.name.replace(' ', '_')}_badge",
                image=image,
                reason=f"Updating Badge Called {request_badge.name}",
            )
            emoji_str = f"<:{new_emoji.name}:{new_emoji.id}>"

        await badge_manager.update_badge(
            badge_id,
            name=request_badge.name,
            description=request_badge.description,
            icon_url=request_badge.icon_url,
            emoji=emoji_str,
            rarity=Rarity(request_badge.rarity),
            requirements=requirements,
            hidden=request_badge.hidden,
        )

        return {"success": True}

    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code, detail=http_error.detail
        )

    except Exception as e:
        # Log the full exception for debugging
        logger.error(
            f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}"
        )

        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}",
        )


async def deleteBadge(
    badge_id: int, request: Request, guild_id: Optional[int] = None
) -> Dict[str, bool]:
    """Delete a badge"""
    backend: APIServer = request.app.state.backend
    try:
        if not guild_id:
            await check_owner(request)
        badgeManager = BadgeManager(guild_id)
        badge = await badgeManager.get_badge(badge_id)
        if not badge:
            raise HTTPException(
                status_code=404, detail=f"No Badge with the ID {badge_id} found."
            )
        await backend.storage.delete_file(badge.icon_url.split("/")[-1])
        guild = await getGuild(backend.client, guild_id)
        emoji_id = re.search(r"<:\w+:(\d+)>", badge.emoji)
        if not emoji_id:
            raise RuntimeError("Not Expected to not find an emoji id")
        emoji_id = int(emoji_id.group(1))
        emoji = nexon.utils.get(guild.emojis, id=emoji_id)
        if emoji:
            await emoji.delete()
        await badgeManager.delete_badge(badge_id)
        return {"success": True}
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code, detail=http_error.detail
        )

    except Exception as e:
        # Log the full exception for debugging
        logger.error(
            f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}"
        )

        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}",
        )


async def getBadge(badge_id: int, request: Request, guild_id: Optional[int] = None):
    """Get detailed information about a specific badge"""
    try:
        if not guild_id:
            await check_owner(request)
        badge = await BadgeManager(guild_id).get_badge(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail="Badge not found")
        return await badge.to_dict()
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code, detail=http_error.detail
        )

    except Exception as e:
        # Log the full exception for debugging
        logger.error(
            f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}"
        )

        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}",
        )
