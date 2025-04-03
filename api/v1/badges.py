import re
from fastapi import HTTPException, Request
from typing import TYPE_CHECKING, Optional

from nexon import ComparisonType, Rarity, RequirementType
from nexon.ext.commands import Bot
import nexon
from api.v1.auth import check_owner
from modules.Nexon import download_image_to_bytes
from .baseModels import *
from nexon.badge import BadgeManager
import logging

if TYPE_CHECKING:
    from classes.Other.Dashboard import DashboardCog
    
async def getGuild(client: Bot, id: Optional[int]):
    guild = client.get_guild(1262297191884521514) if not id else client.get_guild(id)
    if not guild:
        guild = await client.fetch_guild(1262297191884521514) if not id else await client.fetch_guild(id)
    return guild

async def check_guild(guild_id: int):
    badges = await BadgeManager(guild_id).get_all_badges() or []
    if len(badges) >= 8:
        raise HTTPException(
            status_code=403,
            detail="You have exceeded the maximum badge limit for the Free Tier."
        )

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("bot")

async def createBadge(request: Request, badge_request: CreateBadgeRequest, guild_id: Optional[int] = None):
    """Create a new badge"""
    backend: DashboardCog = request.app.state.backend
    try:
        # Convert dictionary requirements to BadgeRequirement objects
        if guild_id:
            await check_guild(guild_id)
        elif request:
            await check_owner(request)
        
        requirements: list[tuple[RequirementType, ComparisonType, str]] = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value")), 
            ) for req in badge_request.requirements
        ]
        guild = await getGuild(backend.client, guild_id)
        image = download_image_to_bytes(badge_request.icon_url)
        if not image:
            raise Exception("No image founded")
        emoji = await guild.create_custom_emoji(
            name=f"{badge_request.name.replace(" ", "_")}_badge",
            image=image,
            reason=f"Creating New Badge Called {badge_request.name}"
        )
        await BadgeManager(guild_id).create_badge(name=badge_request.name,
            description=badge_request.description,
            icon_url=badge_request.icon_url,
            emoji=f"<:{emoji.name}:{emoji.id}>",
            rarity=Rarity(badge_request.rarity),
            requirements=requirements,
            hidden=badge_request.hidden)
        return {"success": True}
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail
        )
    
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, guild_id: {guild_id}")
        
        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}"
        )


async def getBadges(request: Request, guild_id: Optional[int] = None):
    """Get all badges"""
    try:
        
        if not guild_id:
            await check_owner(request)
        
        badge_manager = BadgeManager(guild_id)
        badges = await badge_manager.get_all_badges()
        # Convert badges to a list of dictionaries, handling each badge individually
        badge_list = []
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
            status_code=http_error.status_code,
            detail=http_error.detail
        )
    
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, guild_id: {guild_id}")
        
        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}"
        )


async def editBadge(badge_id: int, request: Request, request_badge: CreateBadgeRequest, guild_id: Optional[int] = None):
    """Edit an existing badge"""
    try:
        backend: DashboardCog = request.app.state.backend
        if not guild_id:
            await check_owner(request)
        
        badge_manager = BadgeManager(guild_id)
        
        # Convert requirements
        requirements = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value"))
            ) for req in request_badge.requirements
        ]
        
        # Handle emoji update if icon changed
        existing_badge = await badge_manager.get_badge(badge_id)
        if not existing_badge:
            raise HTTPException(status_code=404, detail="Badge not found")
        
        emoji_str = existing_badge.emoji
        if existing_badge.icon_url != request_badge.icon_url:
            guild = await getGuild(backend.client, guild_id)
            
            # Delete old image and emoji
            backend.delete_image(existing_badge.icon_url.split("/")[-1])
            emoji_id = re.search(r"<:\w+:(\d+)>", existing_badge.emoji)
            if emoji_id:
                emoji_id = int(emoji_id.group(1))
                emoji = nexon.utils.get(guild.emojis, id=emoji_id)
                if emoji:
                    await emoji.delete()
            
            # Create new emoji
            image = download_image_to_bytes(request_badge.icon_url)
            if not image:
                raise Exception("No image found")
            new_emoji = await guild.create_custom_emoji(
                name=f"{request_badge.name.replace(' ', '_')}_badge",
                image=image,
                reason=f"Updating Badge Called {request_badge.name}"
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
            hidden=request_badge.hidden
        )
        
        return {"success": True}
        
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail
        )
    
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}")
        
        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}"
        )


async def deleteBadge(badge_id: int, request: Request, guild_id: Optional[int] = None):
    """Delete a badge"""
    backend: DashboardCog = request.app.state.backend
    try:
        if not guild_id:
            await check_owner(request)
        badgeManager = BadgeManager(guild_id)
        badge = await badgeManager.get_badge(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail=f"No Badge with the ID {badge_id} found.")
        backend.delete_image(badge.icon_url.split("/")[-1])
        guild = await getGuild(backend.client, guild_id)
        emoji_id = re.search(r"<:\w+:(\d+)>", badge.emoji)
        if not emoji_id:
            raise RuntimeError("Not Expected to not find an emoji id")
        emoji_id = int(emoji_id.group(1))
        emoji = nexon.utils.get(guild.emojis, id=emoji_id)
        if not emoji:
            raise ValueError("Couldn't Find Emoji")
        await emoji.delete()
        await badgeManager.delete_badge(badge_id)
        return {"success": True}
    except HTTPException as http_error:
        # Capture and re-raise HTTP exceptions with more detail
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail
        )
    
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}")
        
        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}"
        )

async def getBadge(badge_id: int, request:Request, guild_id: Optional[int] = None):
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
            status_code=http_error.status_code,
            detail=http_error.detail
        )
    
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Unexpected error: {e}, badge_id: {badge_id}, guild_id: {guild_id}")
        
        # Raise a more detailed error response
        raise HTTPException(
            status_code=400,
            detail=f"An unexpected error occurred while fetching the badge. Error: {str(e)}"
        )