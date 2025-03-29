import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING

from nexon import ComparisonType, File, Rarity, RequirementType
import nexon
from modules.Nexon import download_image_to_bytes, overwriteOwner
from .baseModels import *
from nexon.badge import BadgeManager

if TYPE_CHECKING:
    from ...classes.Other.Dashboard import DashboardCog

router = APIRouter()


@router.get("/is_owner")
async def is_owner(request: Request):
    """Check if the authenticated user is the bot owner"""
    backend: DashboardCog = request.app.state.backend
    try:
        # Verify authentication and get access token
        access_token = await backend.verify_auth(request)
        
        # Get user from cache or Discord API
        if access_token in backend.user_cache:
            user = backend.user_cache[access_token]
        else:
            user = await backend.rate_limited_request(
                "/users/@me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            backend.user_cache[access_token] = user
        
        # Check if user is owner
        user_id = int(user["id"])
        is_owner = user_id == overwriteOwner or user_id == backend.client.owner_id
        
        return JSONResponse({
            "is_owner": is_owner,
            "user_id": user_id
        })
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
@router.post("/stats")
async def get_admin_stats(request: Request):
    """Get detailed bot statistics for admin"""
    backend: DashboardCog = request.app.state.backend
    try:
        # Get total badges
        badge_manager = BadgeManager()
        badges = await badge_manager.get_all_badges()
        total_badges = len(badges)

        # Get total servers
        total_servers = len(backend.client.guilds)

        # Calculate active users (unique users across all guilds)
        active_users = set()
        for guild in backend.client.guilds:
            for member in guild.members:
                active_users.add(member.id)

        return {
            "total_badges": total_badges,
            "total_servers": total_servers,
            "active_users": len(active_users)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def check_owner(request: Request):
    backend: DashboardCog = request.app.state.backend
    access_token = await backend.verify_auth(request)
    if access_token in backend.user_cache:
        user = backend.user_cache[access_token]
    else:
        user = await backend.rate_limited_request(
            "/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        backend.user_cache[access_token] = user
    user_id = int(user["id"])
    if user_id != overwriteOwner and user_id != backend.client.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.post("/badges/create")
async def create_badge(request: Request, badge_request: CreateBadgeRequest):
    """Create a new badge"""
    backend: DashboardCog = request.app.state.backend
    try:
        # Convert dictionary requirements to BadgeRequirement objects
        await check_owner(request)
        
        requirements: list[tuple[RequirementType, ComparisonType, str]] = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value")), 
            ) for req in badge_request.requirements
        ]
        guild = backend.client.get_guild(1262297191884521514)
        if not guild:
            guild = await backend.client.fetch_guild(1262297191884521514)
        image = download_image_to_bytes(badge_request.icon_url)
        if not image:
            raise Exception("No image founded")
        emoji = await guild.create_custom_emoji(
            name=f"{badge_request.name.replace(" ", "_")}_badge",
            image=image,
            reason=f"Creating New Badge Called {badge_request.name}"
        )
        # <:9473f46e80349ffde33845582cd9f65f:1355397901119000717>
        await BadgeManager().create_badge(name=badge_request.name,
            description=badge_request.description,
            icon_url=badge_request.icon_url,
            emoji=f"<:{emoji.name}:{emoji.id}>",
            rarity=Rarity(badge_request.rarity),
            requirements=requirements,
            hidden=badge_request.hidden)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/badges")
async def get_badges(request: Request):
    """Get all badges"""
    try:
        
        await check_owner(request)
        
        badge_manager = BadgeManager()
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/badges/{badge_id}")
async def edit_badge(badge_id: int, request: Request, request_badge: CreateBadgeRequest):
    """Edit an existing badge"""
    try:
        backend: DashboardCog = request.app.state.backend
        await check_owner(request)
        
        badge_manager = BadgeManager()
        
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
            guild = backend.client.get_guild(1262297191884521514)
            if not guild:
                guild = await backend.client.fetch_guild(1262297191884521514)
            
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
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/badges/{badge_id}")
async def delete_badge(badge_id: int, request: Request):
    """Delete a badge"""
    backend: DashboardCog = request.app.state.backend
    try:
        await check_owner(request)
        badgeManager = BadgeManager()
        badge = await badgeManager.get_badge(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail=f"No Badge with the ID {badge_id} found.")
        backend.delete_image(badge.icon_url.split("/")[-1])
        guild = backend.client.get_guild(1262297191884521514)
        if not guild:
            guild = await backend.client.fetch_guild(1262297191884521514)
        emoji_id = re.search(r"<:\w+:(\d+)>", badge.emoji)
        if not emoji_id:
            raise RuntimeError("Not Expected to not find an emoji id")
        emoji_id = int(emoji_id.group(1))
        emoji = nexon.utils.get(guild.emojis, id=emoji_id)
        if not emoji:
            raise ValueError("Couldn't Find Emoji")
        await emoji.delete()
        await BadgeManager().delete_badge(badge_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/badges/{badge_id}")
async def get_badge(badge_id: int, request:Request):
    """Get detailed information about a specific badge"""
    try:
        await check_owner(request)
        badge = await BadgeManager().get_badge(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail="Badge not found")
        return await badge.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))