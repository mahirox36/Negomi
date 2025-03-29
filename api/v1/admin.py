from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING

from nexon import ComparisonType, Rarity, RequirementType
from modules.Nexon import overwriteOwner
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
        await BadgeManager().create_badge(name=badge_request.name,
            description=badge_request.description,
            icon_url=badge_request.icon_url,
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
        badges = await BadgeManager().get_all_badges()
        return {"badges": [badge.to_dict() for badge in badges]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/badges/{badge_id}/edit")
async def edit_badge(badge_id: int,request: Request, request_badge: CreateBadgeRequest):
    """Edit an existing badge"""
    try:
        await check_owner(request)
        # Convert dictionary requirements to BadgeRequirement objects
        requirements: list[tuple[RequirementType, ComparisonType, str]] = [
            (
                RequirementType(req.get("type")),
                ComparisonType(req.get("comparison")),
                str(req.get("value")), 
            ) for req in request_badge.requirements
        ]
        
        await BadgeManager().update_badge(badge_id,
                                          name=request_badge.name,
                                            description=request_badge.description,
                                            icon_url=request_badge.icon_url,
                                            rarity=Rarity(request_badge.rarity),
                                            requirements=requirements,
                                            hidden=request_badge.hidden
                                            )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/badges/{badge_id}/delete")
async def delete_badge(badge_id: int, request: Request):
    """Delete a badge"""
    try:
        await check_owner(request)
        await BadgeManager().delete_badge(badge_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/badges/{badge_id}")
async def get_badge(badge_id: int):
    """Get detailed information about a specific badge"""
    try:
        badge = await BadgeManager().get_badge(badge_id)
        if not badge:
            raise HTTPException(status_code=404, detail="Badge not found")
        return badge.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))