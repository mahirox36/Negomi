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

@router.post("/badges/create")
async def create_badge(request: Request, badge_request: CreateBadgeRequest):
    """Create a new badge"""
    return await createBadge(request, badge_request)

@router.get("/badges")
async def get_badges(request: Request):
    """Get all badges"""
    return await getBadges(request)

@router.put("/badges/{badge_id}")
async def edit_badge(badge_id: int, request: Request, request_badge: CreateBadgeRequest):
    """Edit an existing badge"""
    return await editBadge(badge_id, request, request_badge)

@router.delete("/badges/{badge_id}")
async def delete_badge(badge_id: int, request: Request):
    """Delete a badge"""
    return await deleteBadge(badge_id, request)

@router.get("/badges/{badge_id}")
async def get_badge(badge_id: int, request:Request):
    """Get detailed information about a specific badge"""
    return await getBadge(badge_id, request)