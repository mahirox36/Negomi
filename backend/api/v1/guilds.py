from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING
from nexon import ChannelType

from .badges import *
from .baseModels import *
from .layout import pages
from nexon import Feature
if TYPE_CHECKING:
    from backend.apiManager import APIServer

router = APIRouter(tags=["guilds"])

@router.get("/")
async def get_guilds(request: Request):
    """Get summary of the top 10 most popular guilds by member count"""
    backend: APIServer = request.app.state.backend
    guilds = sorted(
        backend.client.guilds, 
        key=lambda g: g.member_count if g.member_count is not None else 0, 
        reverse=True
    )[:10]
    return {
        "guilds": [
            {
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count,
                "icon_url": str(guild.icon.url) if guild.icon else None,
                "owner_id": guild.owner_id,
                "boost_level": guild.premium_tier,
                "boost_count": guild.premium_subscription_count,
                "verification_level": str(guild.verification_level),
                "features": guild.features,
                "created_at": guild.created_at.timestamp(),
                "channel_count": len(guild.channels),
                "role_count": len(guild.roles),
                "emoji_count": len(guild.emojis)
            } for guild in guilds
        ]
    }

@router.get("/{guild_id}")
async def get_guild(guild_id: int, request: Request):
    """Get detailed information about a specific guild"""
    backend: APIServer = request.app.state.backend
    guild = await backend.fetch_guild(guild_id)
    
    return {
        "id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
        "channel_count": len(guild.channels),
        "role_count": len(guild.roles),
        "emoji_count": len(guild.emojis),
        "features": guild.features,
        "created_at": guild.created_at.timestamp(),
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "boost_level": guild.premium_tier,
        "boost_count": guild.premium_subscription_count,
        "verification_level": str(guild.verification_level),
        "owner_id": guild.owner_id
    }

@router.post("/{guild_id}/is_admin")
async def is_admin(guild_id: int, request: Request):
    """Check if the user is an admin in the guild"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get user data
        user = await session.fetch_user()
        
        # Get guild
        guild = await backend.fetch_guild(guild_id)
        member = guild.get_member(int(user["id"]))
        
        if not member:
            return JSONResponse(
                status_code=403,
                content={
                    "isAdmin": False,
                    "detail": "You are not a member of this server. Please join the server first."
                }
            )

        is_admin = member.guild_permissions.administrator
        if not is_admin:
            return JSONResponse(
                status_code=403,
                content={
                    "isAdmin": False,
                    "detail": "You need administrator permissions to access this page."
                }
            )

        return JSONResponse({
            "isAdmin": True,
            "detail": "Access granted"
        })

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code, 
            content={
                "isAdmin": False,
                "detail": str(e.detail)
            }
        )
    except Exception as e:
        backend.logger.error(f"Error checking admin status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "isAdmin": False,
                "detail": "An internal server error occurred"
            }
        )

@router.get("/{guild_id}/channels_names")
async def get_guild_channels_names(guild_id: int, request: Request):
    """Get channel names for a specific guild"""
    backend: APIServer = request.app.state.backend
    guild = await backend.fetch_guild(guild_id)
    
    return [channel.name for channel in guild.channels]

@router.get("/{guild_id}/channels")
async def get_guild_channels(guild_id: int, request: Request):
    """Get channels for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        channels = []
        
        for channel in guild.channels:
            # Filter out categories and threads
            if channel.type not in [ChannelType.category, ChannelType.forum]:
                channels.append({
                    "id": str(channel.id),
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "category": str(channel.category_id) if channel.category_id else None,
                    "is_nsfw": getattr(channel, 'is_nsfw', lambda: False)()
                })
        
        # Sort channels by position and name
        channels.sort(key=lambda x: (x["position"], x["name"]))
        return channels
        
    except Exception as e:
        backend.logger.error(f"Error fetching channels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch channels")

@router.get("/{guild_id}/roles")
async def get_guild_roles(guild_id: int, request: Request):
    """Get roles for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        roles = []
        
        for role in guild.roles:
            # Filter out @everyone role and include only assignable roles
            if not role.is_default():
                if not role.icon:
                    role_icon = None
                else:
                    role_icon = role.icon.url if not isinstance(role.icon, str) else role.icon
                color = f"#{role.color.value:06x}" 
                me = guild.me
                roles.append({
                    "id": str(role.id),
                    "name": role.name,
                    "position": role.position,
                    "color": color,
                    "mentionable": role.mentionable,
                    "managed": role.managed,
                    "permissions": role.permissions.value,
                    "icon": role_icon,
                    "is_assignable": (me.top_role > role or me.id == guild.owner_id)
                })
        
        # Sort roles by position (highest first) and name
        roles.sort(key=lambda x: (-x["position"], x["name"]))
        return roles
        
    except Exception as e:
        backend.logger.error(f"Error fetching roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch roles")

@router.get("/{guild_id}/categories")
async def get_guild_categories(guild_id: int, request: Request):
    """Get categories for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        categories = []
        
        for channel in guild.channels:
            if channel.type == ChannelType.category:
                categories.append({
                    "id": str(channel.id),
                    "name": channel.name,
                    "position": channel.position
                })
        
        # Sort categories by position and name
        categories.sort(key=lambda x: (x["position"], x["name"]))
        return categories
        
    except Exception as e:
        backend.logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/{guild_id}/joined")
async def get_joined_guilds(guild_id: int, request: Request) -> bool:
    """Check if the bot is in a specific guild"""
    backend: APIServer = request.app.state.backend
    return guild_id in [g.id for g in backend.client.guilds]

@router.post("/filter_joined")
async def filter_joined_guilds(request: Request, data: GuildsRequest):
    """Return list of guild IDs that the bot is a member of"""
    backend: APIServer = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Access token is missing")
        session = backend.oauth_sessions[access_token]
        
        # Get user's guilds from OAuth session
        user_guilds = await session.fetch_guilds()
        
        # Filter guilds that the bot is in
        bot_guild_ids = [str(g.id) for g in backend.client.guilds]
        joined_guilds = [
            guild["id"] for guild in user_guilds 
            if guild["id"] in bot_guild_ids and guild["id"] in data.guilds
        ]
        
        return joined_guilds
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to filter guilds")

@router.get("/{guild_id}/settings/{page}")
async def get_settings(guild_id: int, page: str, request: Request):
    """Get saved settings for a specific page"""
    backend: APIServer = request.app.state.backend
    try:
        featureManager = await Feature.get_guild_feature(guild_id, page.replace("-", "_"))
        
        if not page in pages:
            raise HTTPException(status_code=404, detail="Page not found")
        
        return featureManager.get_setting()
        
    except Exception as e:
        backend.logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{guild_id}/settings/{page}")
async def save_settings(guild_id: int, page: str, request: Request):
    """Save all settings for a specific page"""
    backend: APIServer = request.app.state.backend
    try:
        # Get direct settings data from request
        settings = await request.json()
        if isinstance(settings, dict) and settings.get("withCredentials"):
            settings.pop("withCredentials")
        featureManager = await Feature.get_guild_feature(guild_id, page.replace("-", "_"))
        
        featureManager.settings["settings"] = settings
        await featureManager.save()
        
        return {"success": True, "message": "Settings saved successfully"}
        
    except Exception as e:
        backend.logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{guild_id}/settings/{page}")
async def delete_settings(guild_id: int, page: str):
    """Delete all settings for a specific page"""
    try:
        await (await Feature.get_guild_feature(guild_id, page.replace("-", "_"))).delete_class()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Features

@router.post("/{guild_id}/features/{class_name}")
async def set_feature(guild_id: int, class_name: str, request: FeatureSetRequest):
    """Set a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    await featureManager.set_setting(request.feature_name, request.value)
    return {"success": True}

@router.get("/{guild_id}/features/{class_name}")
async def get_feature(guild_id: int, class_name: str, feature_name: str):
    """Get a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    return {feature_name: await featureManager.get_setting(feature_name)}

@router.delete("/{guild_id}/features/{class_name}")
async def reset_feature(guild_id: int, class_name: str, feature_name: str):
    """Reset a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if await featureManager.delete_setting(feature_name):
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Feature not found")

@router.post("/{guild_id}/features/{class_name}/enable")
async def enable_feature(guild_id: int, class_name: str):
    """Enable a class for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if not featureManager.enabled:
        await featureManager.enable()
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Feature already enabled")

@router.post("/{guild_id}/features/{class_name}/disable")
async def disable_feature(guild_id: int, class_name: str):
    """Disable a class for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if featureManager.enabled:
        await featureManager.disable()
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Feature already disabled")

@router.get("/{guild_id}/features/{class_name}/status")
async def get_feature_status(guild_id: int, class_name: str):
    return {"enabled": (await Feature.get_guild_feature(guild_id, class_name)).enabled}       

@router.post("/{guild_id}/badges/create")
async def create_badge(guild_id: int, request: Request, badge_request: CreateBadgeRequest):
    """Create a new badge"""
    return await createBadge(request, badge_request, guild_id) # type: ignore

@router.get("/{guild_id}/badges")
async def get_badges(guild_id: int, request: Request):
    """Get all badges"""
    return await getBadges(request, guild_id) # type: ignore

@router.put("/{guild_id}/badges/{badge_id}")
async def edit_badge(guild_id: int, badge_id: int, request: Request, request_badge: CreateBadgeRequest):
    """Edit an existing badge"""
    return await editBadge(badge_id, request, request_badge, guild_id) # type: ignore

@router.delete("/{guild_id}/badges/{badge_id}")
async def delete_badge(guild_id: int, badge_id: int, request: Request):
    """Delete a badge"""
    return await deleteBadge(badge_id, request, guild_id) # type: ignore

@router.get("/{guild_id}/badges/{badge_id}")
async def get_badge(guild_id: int, badge_id: int, request:Request):
    """Get detailed information about a specific badge"""
    return await getBadge(badge_id, request, guild_id) # type: ignore