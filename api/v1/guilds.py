from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING
from .baseModels import *
from .layout import pages
from nexon import BadgeManager, Feature
if TYPE_CHECKING:
    from ...classes.Other.Dashboard import DashboardCog

router = APIRouter()

@router.get("/")
async def get_guilds(request: Request):
    """Get summary of all guilds"""
    backend: DashboardCog = request.app.state.backend
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
            } for guild in backend.client.guilds
        ]
    }

@router.get("/{guild_id}")
async def get_guild(guild_id: int, request: Request):
    """Get detailed information about a specific guild"""
    backend: DashboardCog = request.app.state.backend
    guild = await backend.get_guild(guild_id)
    
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
    backend: DashboardCog = request.app.state.backend
    try:
        access_token = await backend.verify_auth(request)
        
        # Get user from cache or API
        if access_token in backend.user_cache:
            user = backend.user_cache[access_token]
        else:
            user = await backend.rate_limited_request(
                "/users/@me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            backend.user_cache[access_token] = user

        # Get guild
        guild = await backend.get_guild(guild_id)
        member = guild.get_member(int(user["id"]))
        
        if not member:
            # Return 403 with isAdmin: false to trigger AccessDenied component
            return JSONResponse(
                status_code=403,
                content={
                    "isAdmin": False,
                    "detail": "You are not a member of this server. Please join the server first."
                }
            )

        is_admin = member.guild_permissions.administrator
        if not is_admin:
            # Return 403 with isAdmin: false to trigger AccessDenied component
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
        # Return consistent format for HTTPExceptions
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
                "detail": "An internal server error occurred. Please try again later."
            }
        )

@router.get("/{guild_id}/channels_names")
async def get_guild_channels_names(guild_id: int, request: Request):
    """Get channel names for a specific guild"""
    backend: DashboardCog = request.app.state.backend
    guild = await backend.get_guild(guild_id)
    
    return [channel.name for channel in guild.channels]
@router.get("/{guild_id}/channels")
async def get_guild_channels(guild_id: int, request: Request):
    """Get channels for a specific guild"""
    backend: DashboardCog = request.app.state.backend
    guild = await backend.get_guild(guild_id)
    
    return {
        "channels": [
            {
                "id": channel.id,
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position
            } for channel in guild.channels
        ]
    }

@router.get("/{guild_id}/joined")
async def get_joined_guilds(guild_id: int, request: Request) -> bool:
    """Check if the bot is in a specific guild"""
    backend: DashboardCog = request.app.state.backend
    return guild_id in [g.id for g in backend.client.guilds]


@router.post("/filter_joined")
async def filter_joined_guilds(request: Request, data: GuildsRequest) -> List[str]:
    """Return list of guild IDs that the bot is a member of"""
    backend: DashboardCog = request.app.state.backend
    return [guild for guild in data.guilds if int(guild) in [g.id for g in backend.client.guilds]]

@router.get("/{guild_id}/settings/{page}")
async def get_settings(guild_id: int, page: str, request: Request):
    """Get saved settings for a specific page"""
    backend: DashboardCog = request.app.state.backend
    try:
        featureManager = await Feature.get_guild_feature(guild_id, page.replace("%20", " "))
        settings = {}
        
        # Get the page layout
        normalized_page = page.replace("%20", " ")
        if normalized_page in pages:
            for item in pages[normalized_page]:
                if item["type"] == "panel":
                    for setting in item.get("settings", []):
                        saved_value = featureManager.get_setting(setting["name"])
                        # If no saved value, use the default value from pages
                        settings[setting["name"]] = saved_value if saved_value is not None else setting["value"]
                        backend.logger.info(f"Loading setting {setting['name']}: {settings[setting['name']]} (saved: {saved_value}, default: {setting['value']})")
        
        return {"settings": settings}
    except Exception as e:
        backend.logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{guild_id}/settings/{page}")
async def save_settings(guild_id: int, page: str, request: Request):
    """Save all settings for a specific page"""
    backend: DashboardCog = request.app.state.backend
    try:
        data = await request.json()
        settings = data.get("settings", {})
        featureManager = await Feature.get_guild_feature(guild_id, page)
        
        for setting_name, value in settings.items():
            await featureManager.set_setting(setting_name, value)
        
        return {"success": True}
    except Exception as e:
        backend.logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{guild_id}/settings/{page}")
async def delete_settings(guild_id: int, page: str):
    """Delete all settings for a specific page"""
    try:
        await (await Feature.get_guild_feature(guild_id, page)).delete_class()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Features

@router.post("/{guild_id}/features/{class_name}/set")
async def set_feature(guild_id: int, class_name: str, request: FeatureSetRequest):
    """Set a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    await featureManager.set_setting(request.feature_name, request.value)
    return {"success": True}
@router.get("/{guild_id}/features/{class_name}/get")
async def get_feature(guild_id: int, class_name: str, feature_name: str):
    """Get a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    return {feature_name: await featureManager.get_setting(feature_name)}
@router.post("/{guild_id}/features/{class_name}/reset")
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