import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING

from nexon import ComparisonType, File, Rarity, RequirementType
import nexon
from modules.Nexon import download_image_to_bytes, overwriteOwner
from .baseModels import *
from .badges import *
from nexon.badge import BadgeManager

if TYPE_CHECKING:
    from backend.apiManager import APIServer

router = APIRouter(tags=["admin"])


@router.get("/is_owner")
async def is_owner(request: Request):
    """Check if the authenticated user is the bot owner"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session =  backend.oauth_sessions[access_token]
        
        # Get user from OAuth session
        user = await session.fetch_user()
        user_id = int(user["id"])
        
        # Check if user is owner
        is_owner = user_id == overwriteOwner or user_id ==  backend.client.owner_id
        
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
    backend: APIServer = request.app.state.backend
    await check_owner(request)
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

@router.post("/badges/create")
async def create_badge(request: Request, badge_request: CreateBadgeRequest):
    """Create a new badge"""
    return await createBadge(request, badge_request) # type: ignore

@router.get("/badges")
async def get_badges(request: Request):
    """Get all badges"""
    return await getBadges(request) # type: ignore

@router.put("/badges/{badge_id}")
async def edit_badge(badge_id: int, request: Request, request_badge: CreateBadgeRequest):
    """Edit an existing badge"""
    return await editBadge(badge_id, request, request_badge) # type: ignore

@router.delete("/badges/{badge_id}")
async def delete_badge(badge_id: int, request: Request):
    """Delete a badge"""
    return await deleteBadge(badge_id, request) # type: ignore

@router.get("/badges/{badge_id}")
async def get_badge(badge_id: int, request:Request):
    """Get detailed information about a specific badge"""
    return await getBadge(badge_id, request) # type: ignore

@router.get("/guilds")
async def get_admin_guilds(request: Request):
    """Get summary of all guilds for admin"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get user data and verify owner status
        user = await session.fetch_user()
        user_id = int(user["id"])
        if user_id != overwriteOwner and user_id != backend.client.owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        return {
            "guilds": [
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "icon_url": str(guild.icon.url) if guild.icon else None,
                    "owner_id": str(guild.owner_id),
                    "boost_level": guild.premium_tier,
                    "boost_count": guild.premium_subscription_count,
                    "verification_level": str(guild.verification_level),
                    "features": guild.features,
                    "created_at": guild.created_at.timestamp(),
                    "channel_count": len(guild.channels),
                    "role_count": len(guild.roles),
                    "emoji_count": len(guild.emojis)
                } for guild in backend.client.guilds
            ]
        }
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": str(e.detail)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to fetch guilds"}
        )