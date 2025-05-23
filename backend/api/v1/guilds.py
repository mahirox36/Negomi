import base64
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from nexon import ChannelType, utils
from nexon.channel import CategoryChannel, TextChannel
from nexon.data.models import Messages
from nexon.embeds import Embed
from nexon.types.oauth2 import User
from .badges import *
from .baseModels import *
from .baseModels import *
from .layout import pages
from nexon import Feature
from nexon.data.models import MemberData
from pydantic import BaseModel, Field
from typing import List, Union
from nexon import Logs


if TYPE_CHECKING:
    from classes.Features.Welcome import Welcome
    from backend.apiManager import APIServer
import re

router = APIRouter(tags=["guilds"])
# check if 


async def get_user(request: Request, guild_id: Optional[int] = None) -> User:
    """Retrieve the authenticated user from the request and check if they are an admin of a specific guild"""
    backend: APIServer = request.app.state.backend
    access_token = await backend.verify_auth(request)
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Use cached user data
    cached_user = await backend.cache.get_cached_user(access_token)
    if cached_user:
        user = User(**cached_user)  # Convert cached data to User object
    else:
        session = backend.oauth_sessions[access_token]
        user = await session.fetch_user()

    if guild_id is not None:
        guild = await backend.fetch_guild(guild_id)
        member = guild.get_member(int(user["id"] if isinstance(user, dict) else user.id))
        if not member:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this server. Please join the server first.",
            )
        if not member.guild_permissions.administrator:
            raise HTTPException(
                status_code=403,
                detail="You need administrator permissions to access this resource.",
            )

    return user


@router.get("/guilds")
async def get_guilds(request: Request):
    """Get summary of the top 10 most popular guilds by member count, excluding a specific guild"""
    backend: APIServer = request.app.state.backend
    excluded_guild_id = 333949691962195969
    guilds = sorted(
        [g for g in backend.client.guilds if g.id != excluded_guild_id],
        key=lambda g: g.member_count if g.member_count is not None else 0,
        reverse=True,
    )[:10]
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
                "emoji_count": len(guild.emojis),
            }
            for guild in guilds
        ]
    }


@router.get("/{guild_id}")
async def get_guild(guild_id: int, request: Request):
    """Get detailed information about a specific guild including statistics"""
    backend: APIServer = request.app.state.backend
    guild = await backend.fetch_guild(guild_id)

    # Fetch basic guild data
    guild_data = {
        "id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
        "channel_count": len(guild.channels),
        "role_count": len(guild.roles),
        "emoji_count": len(guild.emojis),
        "features": guild.features,
        "created_at": guild.created_at.timestamp(),
        "icon_url": (
            str(
                guild.icon.with_size(4096).url.replace(".png", ".gif")
                if guild.icon.is_animated()
                else guild.icon.with_size(4096).url
            )
            if guild.icon
            else None
        ),
        "boost_level": guild.premium_tier,
        "boost_count": guild.premium_subscription_count,
        "verification_level": str(guild.verification_level),
        "owner_id": guild.owner_id,
    }

    # Fetch member statistics from the database

    members_data = await MemberData.filter(guild_id=guild_id)

    total_messages = sum(member.total_messages for member in members_data)
    total_commands = sum(member.commands_used_count for member in members_data)
    total_chars = sum(member.character_count for member in members_data)
    total_attachments = sum(member.attachment_count for member in members_data)

    # Get command usage breakdown
    command_usage = {}
    for member in members_data:
        for cmd, count in member.favorites_commands.items():
            command_usage[cmd] = command_usage.get(cmd, 0) + count

    # Add statistics to response
    guild_data.update(
        {
            "statistics": {
                "total_messages": total_messages,
                "total_commands_used": total_commands,
                "total_characters": total_chars,
                "total_attachments": total_attachments,
                "command_usage": command_usage,
                "active_members": len(members_data),
                "average_messages_per_member": (
                    total_messages / len(members_data) if members_data else 0
                ),
            }
        }
    )

    return guild_data


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
                    "detail": "You are not a member of this server. Please join the server first.",
                },
            )

        is_admin = member.guild_permissions.administrator
        if not is_admin:
            return JSONResponse(
                status_code=403,
                content={
                    "isAdmin": False,
                    "detail": "You need administrator permissions to access this page.",
                },
            )

        return JSONResponse({"isAdmin": True, "detail": "Access granted"})

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"isAdmin": False, "detail": str(e.detail)},
        )
    except Exception as e:
        backend.logger.error(f"Error checking admin status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"isAdmin": False, "detail": "An internal server error occurred"},
        )


@router.get("/{guild_id}/channels_names")
async def get_guild_channels_names(
    guild_id: int, request: Request, user: User = Depends(get_user)
) -> list[str]:
    """Get channel names for a specific guild"""
    # Ensure the user is accessed to trigger authentication
    _ = user

    backend: APIServer = request.app.state.backend
    guild = await backend.fetch_guild(guild_id)

    return [channel.name for channel in guild.channels]


@router.get("/{guild_id}/channels")
async def get_guild_channels(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Get channels for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        channels = []

        for channel in guild.channels:
            # Filter out categories and threads
            if channel.type not in [ChannelType.category, ChannelType.forum]:
                channels.append(
                    {
                        "id": str(channel.id),
                        "name": channel.name,
                        "type": str(channel.type),
                        "position": channel.position,
                        "category": (
                            str(channel.category_id) if channel.category_id else None
                        ),
                        "is_nsfw": getattr(channel, "is_nsfw", lambda: False)(),
                    }
                )

        # Sort channels by position and name
        channels.sort(key=lambda x: (x["position"], x["name"]))
        return channels

    except Exception as e:
        backend.logger.error(f"Error fetching channels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch channels")


@router.get("/{guild_id}/roles")
async def get_guild_roles(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
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
                    role_icon = (
                        role.icon.url if not isinstance(role.icon, str) else role.icon
                    )
                color = f"#{role.color.value:06x}"
                me = guild.me
                roles.append(
                    {
                        "id": str(role.id),
                        "name": role.name,
                        "position": role.position,
                        "color": color,
                        "mentionable": role.mentionable,
                        "managed": role.managed,
                        "permissions": role.permissions.value,
                        "icon": role_icon,
                        "is_assignable": (
                            me.top_role > role or me.id == guild.owner_id
                        ),
                    }
                )

        # Sort roles by position (highest first) and name
        roles.sort(key=lambda x: (-x["position"], x["name"]))
        return roles

    except Exception as e:
        backend.logger.error(f"Error fetching roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch roles")


@router.get("/{guild_id}/categories")
async def get_guild_categories(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Get categories for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        categories = [
            {"id": str(channel.id), "name": channel.name, "position": channel.position}
            for channel in guild.channels
            if channel.type == ChannelType.category
        ]

        # Sort categories by position and name
        categories.sort(key=lambda x: (x["position"], x["name"]))
        return categories

    except Exception as e:
        backend.logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


# get server emojis
@router.get("/{guild_id}/emojis")
async def get_guild_emojis(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Get emojis for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        emojis = [
            {
                "id": str(emoji.id),
                "name": emoji.name,
                "url": str(emoji.url),
                "animated": emoji.animated,
            }
            for emoji in guild.emojis
        ]
        return emojis

    except Exception as e:
        backend.logger.error(f"Error fetching emojis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch emojis")


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
            guild["id"]
            for guild in user_guilds
            if guild["id"] in bot_guild_ids and guild["id"] in data.guilds
        ]

        return joined_guilds

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to filter guilds")


@router.get("/{guild_id}/settings/{page}")
async def get_settings(
    guild_id: int, page: str, request: Request, user: User = Depends(get_user)
):
    """Get saved settings for a specific page"""
    backend: APIServer = request.app.state.backend
    try:
        featureManager = await Feature.get_guild_feature(
            guild_id, page.replace("-", "_")
        )

        settings = featureManager.get_setting()

        # Ensure we return data in the format the frontend expects
        if isinstance(settings, dict) and not "settings" in settings:
            return {"settings": settings}
        return settings

    except Exception as e:
        backend.logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{guild_id}/settings/{page}")
async def save_settings(
    guild_id: int, page: str, request: Request, user: User = Depends(get_user)
):
    """Save all settings for a specific page"""
    backend: APIServer = request.app.state.backend
    try:
        await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Update Settings", {"page": page})
        if page.replace("-", "_") == "temp_voice":
            settings = await request.json()
            # Handle special case for temp_voice settings
            channel_id = settings.get("categoryID")
            if not channel_id:
                raise HTTPException(status_code=400, detail="Channel ID is required")

            return await create_temp_voice_channel(guild_id, request, channel_id)
        # Get direct settings data from request
        request_body = await request.body()
        if not request_body:
            # If body is empty, fetch current settings instead of trying to parse empty JSON
            featureManager = await Feature.get_guild_feature(
                guild_id, page.replace("-", "_")
            )
            return {"success": True, "message": "No changes to save"}

        settings = await request.json()
        if isinstance(settings, dict) and settings.get("withCredentials"):
            settings.pop("withCredentials")
        featureManager = await Feature.get_guild_feature(
            guild_id, page.replace("-", "_")
        )

        # Preserve property naming from the frontend
        # Don't convert camelCase to snake_case or modify key names
        featureManager.settings["settings"] = settings
        await featureManager.save()

        return {"success": True, "message": "Settings saved successfully"}

    except Exception as e:
        backend.logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{guild_id}/settings/{page}")
async def reset_settings(
    guild_id: int, page: str, request: Request, user: User = Depends(get_user)
):
    """Reset all settings for a specific page (does not delete the feature/class)"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Reset Settings", {"page": page})
    try:
        feature = await Feature.get_guild_feature(guild_id, page.replace("-", "_"))
        await feature.reset_settings()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Features


@router.post("/{guild_id}/features/{class_name}")
async def set_feature(
    guild_id: int,
    class_name: str,
    feature_set_request: FeatureSetRequest,
    request: Request,
    user: User = Depends(get_user),
):
    """Set a feature for a specific guild"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Update class settings", {"class_name": class_name, "feature_set": feature_set_request})
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    await featureManager.set_setting(
        feature_set_request.feature_name, feature_set_request.value
    )
    return {"success": True}


@router.get("/{guild_id}/features/{class_name}")
async def get_feature(
    guild_id: int,
    class_name: str,
    feature_name: str,
    request: Request,
    user: User = Depends(get_user),
):
    """Get a feature for a specific guild"""
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    return {feature_name: await featureManager.get_setting(feature_name)}


@router.delete("/{guild_id}/features/{class_name}")
async def reset_feature(
    guild_id: int,
    class_name: str,
    feature_name: str,
    request: Request,
    user: User = Depends(get_user),
):
    """Reset a feature for a specific guild"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Reset class settings", {"class_name": class_name})
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if await featureManager.delete_setting(feature_name):
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Feature not found")


@router.post("/{guild_id}/features/{class_name}/enable")
async def enable_feature(
    guild_id: int, class_name: str, request: Request, user: User = Depends(get_user)
):
    """Enable a class for a specific guild"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Enabled class", {"class_name": class_name})
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if not featureManager.enabled:
        await featureManager.enable()
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Feature already enabled")


@router.post("/{guild_id}/features/{class_name}/disable")
async def disable_feature(
    guild_id: int, class_name: str, request: Request, user: User = Depends(get_user)
):
    """Disable a class for a specific guild"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Disabled settings", {"class_name": class_name})
    featureManager = await Feature.get_guild_feature(guild_id, class_name)
    if featureManager.enabled:
        await featureManager.disable()
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Feature already disabled")


@router.get("/{guild_id}/features/{class_name}/status")
async def get_feature_status(
    guild_id: int, class_name: str, request: Request, user: User = Depends(get_user)
):
    return {"enabled": (await Feature.get_guild_feature(guild_id, class_name)).enabled}


@router.post("/{guild_id}/badges/create")
async def create_badge(
    guild_id: int,
    request: Request,
    badge_request: CreateBadgeRequest,
    user: User = Depends(get_user),
):
    """Create a new badge"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Created a Badge", {"badge": badge_request.model_dump()})
    return await createBadge(request, badge_request, guild_id)  # type: ignore


@router.get("/{guild_id}/badges")
async def get_badges(guild_id: int, request: Request, user: User = Depends(get_user)):
    """Get all badges"""
    return await getBadges(request, guild_id)  # type: ignore


@router.put("/{guild_id}/badges/{badge_id}")
async def edit_badge(
    guild_id: int,
    badge_id: int,
    request: Request,
    request_badge: CreateBadgeRequest,
    user: User = Depends(get_user),
):
    """Edit an existing badge"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Updated a Badge", {"badge": request_badge.model_dump()})
    return await editBadge(badge_id, request, request_badge, guild_id)  # type: ignore


@router.delete("/{guild_id}/badges/{badge_id}")
async def delete_badge(
    guild_id: int, badge_id: int, request: Request, user: User = Depends(get_user)
):
    """Delete a badge"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Deleted a Badge", {"id": badge_id})
    return await deleteBadge(badge_id, request, guild_id)  # type: ignore


@router.get("/{guild_id}/badges/{badge_id}")
async def get_badge(
    guild_id: int, badge_id: int, request: Request, user: User = Depends(get_user)
):
    """Get detailed information about a specific badge"""
    return await getBadge(badge_id, request, guild_id)  # type: ignore


async def create_temp_voice_channel(guild_id: int, request: Request, channel_id: str):
    """Create a temporary voice channel category setup"""
    backend: APIServer = request.app.state.backend
    try:
        # Verify user has manage channel permissions
        access_token = await backend.verify_auth(request)
        if access_token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        session = backend.oauth_sessions[access_token]
        user = await session.fetch_user()
        guild = await backend.fetch_guild(guild_id)
        member = guild.get_member(int(user["id"]))

        if not member:
            raise HTTPException(
                status_code=403, detail="You are not a member of this server"
            )

        if not member.guild_permissions.manage_channels:
            raise HTTPException(
                status_code=403,
                detail="You need Manage Channels permission to configure temporary voice",
            )

        feature = await Feature.get_guild_feature(guild_id, "temp_voice")
        categoryID = channel_id

        # Clean up old create channel if it exists
        if feature.get_setting("CreateChannel"):
            try:
                old_channel = guild.get_channel(
                    int(feature.get_setting("CreateChannel"))
                )
                if old_channel:
                    await old_channel.delete(
                        reason="Old temporary voice channel deleted"
                    )
            except Exception as e:
                backend.logger.warning(
                    f"Failed to delete old temp voice channel: {str(e)}"
                )

        if not categoryID:
            raise HTTPException(status_code=400, detail="Category ID is required")

        # Verify category exists and is valid
        category = guild.get_channel(int(categoryID))
        if not category:
            try:
                category = await guild.fetch_channel(int(categoryID))
            except:
                raise HTTPException(status_code=404, detail="Category not found")

        if not isinstance(category, CategoryChannel):
            raise HTTPException(
                status_code=400, detail="Selected channel must be a category"
            )

        # Create the channel with proper permissions
        overwrites = {
            guild.default_role: nexon.PermissionOverwrite(
                connect=True, speak=False, send_messages=False
            ),
            guild.me: nexon.PermissionOverwrite(
                manage_channels=True, move_members=True, manage_permissions=True
            ),
        }

        channel = await guild.create_voice_channel(
            name="➕ Create Voice Channel",
            category=category,
            reason="Temporary voice channel system setup",
            overwrites=overwrites,
        )

        # Save settings
        await feature.set_setting("CategoryChannel", int(categoryID))
        await feature.set_setting("CreateChannel", channel.id)
        await feature.enable()

        return {
            "success": True,
            "message": "Temporary voice system configured successfully",
            "channelId": str(channel.id),
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        backend.logger.error(f"Error configuring temp voice: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to configure temporary voice system"
        )


@router.get("/{guild_id}/temp-voice")
async def get_temp_voice_channel(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Get the temporary voice channel"""
    # backend: APIServer = request.app.state.backend
    feature = await Feature.get_guild_feature(guild_id, "temp_voice")
    return str(feature.get_setting("CategoryChannel"))


# Welcome Feature Models
class WelcomeConfig(BaseModel):
    enabled: bool = False
    channel_id: Optional[str] = None
    style: str = "text"
    embed_color: Optional[str] = None
    embed_title: Optional[str] = None
    message: str = "Welcome {mention} to {server}!"
    image_settings: Optional[dict] = None


class WelcomePreviewResponse(BaseModel):
    image: Optional[str] = None
    settings: dict
    message: Optional[str] = None


@router.get("/{guild_id}/welcome/settings", response_model=WelcomeConfig)
async def get_welcome_settings(
    request: Request, guild_id: int, user: User = Depends(get_user)
):
    """Get welcome settings for a guild"""
    backend: APIServer = request.app.state.backend
    try:
        # Get the welcome cog
        cog: Optional["Welcome"] = backend.client.get_cog("Welcome")  # type: ignore
        if not cog:
            raise HTTPException(status_code=503, detail="Welcome system not available")

        settings = await cog.config_manager.get_welcome_config(guild_id)
        if not settings:
            return WelcomeConfig()  # Return default settings

        # Ensure embed_color is either a string or None
        if (
            "embed_color" in settings
            and settings["embed_color"] is not None
            and not isinstance(settings["embed_color"], str)
        ):
            settings["embed_color"] = str(settings["embed_color"])

        return WelcomeConfig(**settings)

    except HTTPException as he:
        raise he
    except Exception as e:
        backend.logger.error(f"Error getting welcome settings: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve welcome settings"
        )


@router.post("/{guild_id}/welcome/settings")
async def save_welcome_settings(
    request: Request,
    guild_id: int,
    settings: WelcomeConfig,
    user: User = Depends(get_user),
):
    """Save welcome settings for a guild"""
    backend: APIServer = request.app.state.backend

    try:
        guild = backend.client.get_guild(guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        # Validate channel if enabled
        if settings.enabled:
            if not settings.channel_id:
                raise HTTPException(
                    status_code=400,
                    detail="Channel ID is required when welcome is enabled",
                )

            channel = guild.get_channel(int(settings.channel_id))
            if not channel:
                raise HTTPException(
                    status_code=404, detail="Selected channel not found"
                )

            # Check bot permissions
            permissions = channel.permissions_for(guild.me)
            if not permissions.send_messages:
                raise HTTPException(
                    status_code=403,
                    detail="Bot lacks permission to send messages in channel",
                )

        # Save settings
        welcome = await Feature.get_guild_feature(guild_id, "Welcome")
        if not welcome:
            raise HTTPException(
                status_code=404, detail="Welcome feature not initialized"
            )

        await welcome.set_setting("settings", settings.dict())

        return JSONResponse(
            {"success": True, "message": "Welcome settings saved successfully"}
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error saving welcome settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save welcome settings")


@router.get("/{guild_id}/welcome/preview", response_model=WelcomePreviewResponse)
async def get_welcome_preview(
    request: Request, guild_id: int, user: User = Depends(get_user)
):
    """Generate a welcome message preview"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        cog: Optional["Welcome"] = backend.client.get_cog("Welcome")  # type: ignore
        if not cog:
            raise HTTPException(status_code=503, detail="Welcome system not available")

        config = await cog.config_manager.get_welcome_config(guild_id)
        if not config:
            return WelcomePreviewResponse(settings=WelcomeConfig().dict())

        # Generate preview
        member = guild.me
        welcome_image = await cog.image_generator.create_welcome_image(
            member.display_name,
            str(member.avatar.url) if member.avatar else "",
            config.get("image_settings", {}),
        )

        welcome_image.seek(0)
        image_base64 = base64.b64encode(welcome_image.read()).decode()

        return WelcomePreviewResponse(
            image=f"data:image/png;base64,{image_base64}",
            settings=config,
            message=await cog.format_welcome_message(member, config.get("message", "")),
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        backend.logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")


@router.post("/{guild_id}/welcome/test")
async def test_welcome_message(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Send a test welcome message"""
    backend: APIServer = request.app.state.backend
    try:
        cog: Optional["Welcome"] = backend.client.get_cog("Welcome")  # type: ignore
        if not cog:
            raise HTTPException(status_code=503, detail="Welcome system not available")

        guild = await backend.fetch_guild(guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")

        config = await cog.config_manager.get_welcome_config(guild_id)
        if not config:
            raise HTTPException(status_code=404, detail="Welcome not configured")

        if not config.get("enabled", False):
            raise HTTPException(status_code=400, detail="Welcome system is disabled")

        channel_id = config.get("channel_id")
        if not channel_id:
            raise HTTPException(
                status_code=400, detail="Welcome channel not configured"
            )

        channel = guild.get_channel(int(channel_id))
        if not channel or not isinstance(channel, TextChannel):
            raise HTTPException(
                status_code=404, detail="Welcome channel not found or invalid"
            )

        # Send test message
        await cog.send_welcome_message(guild.me, channel, config)

        return JSONResponse(
            {
                "success": True,
                "message": f"Test welcome message sent to #{channel.name}",
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        backend.logger.error(f"Error sending test: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test message")


@router.get("/{guild_id}/welcome/fonts")
async def get_available_fonts():
    """Get list of available fonts for welcome messages"""
    return {
        "fonts": [
            {
                "name": "Arial",
                "value": "arial",
                "preview_url": "https://example.com/fonts/arial.png",
            },
            {
                "name": "Roboto",
                "value": "roboto",
                "preview_url": "https://example.com/fonts/roboto.png",
            },
            {
                "name": "Open Sans",
                "value": "opensans",
                "preview_url": "https://example.com/fonts/opensans.png",
            },
            {
                "name": "Montserrat",
                "value": "montserrat",
                "preview_url": "https://example.com/fonts/montserrat.png",
            },
        ]
    }


# Message Manager
@router.post("/{guild_id}/messages/create")
async def create_message(
    guild_id: int,
    request: Request,
    message_request: MessageRequest,
    user: User = Depends(get_user),
):
    """Create a new message in a specific channel"""
    backend: APIServer = request.app.state.backend
    try:
        guild = await backend.fetch_guild(guild_id)
        member = guild.get_member(int(user["id"]))

        if not member:
            raise HTTPException(
                status_code=403, detail="You are not a member of this server"
            )

        message = await Messages.create_message(
            name=message_request.name,
            user_id=int(user["id"]),
            guild_id=guild_id,
            channel_id=int(message_request.channel_id),
            content=message_request.content,
            embeds=message_request.embeds,
        )

        # Validate channel ID
        channel = guild.get_channel(int(message_request.channel_id))
        if not channel or not isinstance(channel, TextChannel):
            raise HTTPException(status_code=404, detail="Channel not found")

        await Logs.Logger(
                await backend.fetch_guild(guild_id),
                await backend.fetch_user(int(user["id"])),
            ).info("User Created a Message", {"id": message.id,"message": message_request.model_dump()})
        return JSONResponse(
            {"success": True, "message": "Message created successfully"}
        )

    except Exception as e:
        backend.logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create message")


@router.get("/{guild_id}/messages")
async def get_messages(guild_id: int, request: Request, user: User = Depends(get_user)):
    """Get all messages for a specific guild"""
    backend: APIServer = request.app.state.backend
    try:
        messages = await Messages.get_messages_by_guild(guild_id)
        return [message.to_dict() for message in messages]

    except Exception as e:
        backend.logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")


@router.delete("/{guild_id}/messages/{id}")
async def delete_message(
    guild_id: int, id: int, request: Request, user: User = Depends(get_user)
):
    """Delete a message by ID"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Deleted a Message", {"id": id})
    try:
        message = await Messages.get_or_none(id=id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        # check if the message is avalialbe or not found in discord:
        messageDiscord = await backend.fetch_message(
            message.message_id, message.channel_id
        )
        if not messageDiscord:
            message.message_id = 0
            await message.save()

        if message.is_sent:
            guild = await backend.fetch_guild(guild_id)
            channel = guild.get_channel(int(message.channel_id))
            if not channel or not isinstance(channel, TextChannel):
                try:
                    channel = await guild.fetch_channel(int(message.channel_id))
                except:
                    raise HTTPException(status_code=404, detail="Channel not found")
            # Check if the bot has permission to delete messages
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.manage_messages:
                raise HTTPException(
                    status_code=403,
                    detail="Bot lacks permission to delete messages in this channel",
                )
            if not isinstance(channel, TextChannel):
                raise HTTPException(
                    status_code=400,
                    detail="Selected channel must be a text channel",
                )
            # Delete the message
            try:
                messageDiscord = await channel.fetch_message(message.message_id)
                await messageDiscord.delete()
            except nexon.NotFound:
                pass
            except Exception as e:
                backend.logger.error(f"Error deleting message: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to delete message")
        await message.delete()

        return JSONResponse(
            {"success": True, "message": "Message deleted successfully"}
        )
    except Exception as e:
        backend.logger.error(f"Error deleting message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete message")


@router.get("/{guild_id}/messages/{id}")
async def get_message(
    guild_id: int, id: int, request: Request, user: User = Depends(get_user)
):
    """Get a message by ID"""
    backend: APIServer = request.app.state.backend
    try:
        message = await Messages.get_or_none(id=id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        if not message.message_id:
            return message.to_dict()

        guild = await backend.fetch_guild(guild_id)
        channel = guild.get_channel(int(message.channel_id))
        if not channel or not isinstance(channel, TextChannel):
            try:
                channel = await guild.fetch_channel(int(message.channel_id))
            except:
                message.message_id = 0
            await message.save()
            return message.to_dict()

        try:
            await channel.fetch_message(message.message_id)
        except nexon.NotFound:
            message.message_id = 0
            await message.save()

        return message.to_dict()

    except Exception as e:
        backend.logger.error(f"Error fetching message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch message")


@router.put("/{guild_id}/messages/{id}")
async def update_message(
    guild_id: int,
    id: int,
    request: Request,
    message_request: MessageRequest,
    user: User = Depends(get_user),
):
    """Update a message by ID"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Updated a Message", {"id": id, "message": message_request.model_dump()})
    try:
        message = await Messages.get_or_none(id=id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Update the message content and embeds
        message.content = message_request.content
        message.embeds = message_request.embeds
        await message.save()

        if message.is_sent:
            guild = await backend.fetch_guild(guild_id)
            channel = guild.get_channel(int(message.channel_id))
            if not channel or not isinstance(channel, TextChannel):
                try:
                    channel = await guild.fetch_channel(int(message.channel_id))
                except:
                    raise HTTPException(status_code=404, detail="Channel not found")
            # Check if the bot has permission to edit messages
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.manage_messages:
                raise HTTPException(
                    status_code=403,
                    detail="Bot lacks permission to edit messages in this channel",
                )
            # Edit the message
            if not isinstance(channel, TextChannel):
                raise HTTPException(
                    status_code=400,
                    detail="Selected channel must be a text channel",
                )
            messageDiscord = await channel.fetch_message(message.message_id)
            await messageDiscord.edit(
                content=message.content.format(
                    server=guild.name,
                    channel=channel.mention,
                    memberCount=guild.member_count,
                    date=f"<t:{int(utils.utcnow().timestamp())}:d>",
                    time=f"<t:{int(utils.utcnow().timestamp())}:t>",
                    boostCount=guild.premium_subscription_count,
                    roleCount=len(guild.roles),
                    channelCount=len(guild.channels),
                    emojiCount=len(guild.emojis),
                    owner=guild.owner.display_name if guild.owner else "Unknown",
                    verificationLevel=str(guild.verification_level),
                    createdAt=f"<t:{int(guild.created_at.timestamp())}:R>",
                ),
                embeds=[
                    Embed.from_dict(
                        {**embed, "color": int(embed["color"].lstrip("#"), 16)}
                        if "color" in embed and isinstance(embed["color"], str)
                        else embed
                    )
                    for embed in (message.embeds or [])
                ],
            )

        return JSONResponse(
            {"success": True, "message": "Message updated successfully"}
        )
    except Exception as e:
        backend.logger.error(f"Error updating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update message")


@router.post("/{guild_id}/messages/{id}/send")
async def send_message(
    guild_id: int, id: int, request: Request, user: User = Depends(get_user)
):
    """Send a message by ID"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Sent a Message", {"id": id})
    try:
        message = await Messages.get_or_none(id=id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        if message.is_sent:
            raise HTTPException(status_code=400, detail="Message already sent")

        guild = await backend.fetch_guild(int(guild_id))
        channel = guild.get_channel(int(message.channel_id))
        if not channel or not isinstance(channel, TextChannel):
            raise HTTPException(status_code=404, detail="Channel not found")

        # Check if the bot has permission to send messages
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.send_messages:
            raise HTTPException(
                status_code=403,
                detail="Bot lacks permission to send messages in this channel",
            )

        # Send the message
        message_id = await channel.send(
            message.content.format(
                server=guild.name,
                channel=channel.mention,
                memberCount=guild.member_count,
                date=f"<t:{int(utils.utcnow().timestamp())}:d>",
                time=f"<t:{int(utils.utcnow().timestamp())}:t>",
                boostCount=guild.premium_subscription_count,
                roleCount=len(guild.roles),
                channelCount=len(guild.channels),
                emojiCount=len(guild.emojis),
                owner=guild.owner.display_name if guild.owner else "Unknown",
                verificationLevel=str(guild.verification_level),
                createdAt=f"<t:{int(guild.created_at.timestamp())}:R>",
            ),
            embeds=[
                Embed.from_dict(
                    {**embed, "color": int(embed["color"].lstrip("#"), 16)}
                    if "color" in embed and isinstance(embed["color"], str)
                    else embed
                )
                for embed in message.embeds
            ],
        )

        message.message_id = message_id.id
        await message.save()

        return JSONResponse({"success": True, "message": "Message sent successfully"})
    except Exception as e:
        backend.logger.error(
            f"Error sending message with ID {id} in guild {guild_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to send message")


# Reaction Roles: Works with message framework


class ReactionRoleRequest(BaseModel):
    message_id: int = Field(..., description="ID of the message to add reactions to")
    reactions: List[dict] = Field(
        ...,
        description="List of reaction-role pairs, e.g., [{'emoji': '😊', 'role_id': 123456789}]",
    )
    allow_unselect: bool = False
    max_reactions_per_user: Optional[int] = Field(
        None,
        description="Maximum number of reactions a user can select for this message",
    )
    require_roles: Optional[List[int]] = Field(
        None,
        description="List of role IDs required for a user to interact with the reactions",
    )
    forbidden_roles: Optional[List[int]] = Field(
        None,
        description="List of role IDs that prevent a user from interacting with the reactions",
    )
    cooldown: Optional[int] = Field(
        None,
        description="Cooldown time in seconds before a user can interact with the reactions again",
    )
    remove_reactions: Optional[bool] = Field(
        None,
        description="Whether to remove reaction that the user have selected from the message after a user interacts with them",
    )


@router.post("/{guild_id}/reaction-roles")
async def create_reaction_roles(
    guild_id: int,
    request: Request,
    reaction_role_request: ReactionRoleRequest,
    user: User = Depends(get_user),
):
    """Create or update reaction roles with enhanced validation and support for custom emojis. Adds missing reactions if already present."""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Deleted a Message", {"message_id": reaction_role_request.message_id, "reaction_role": reaction_role_request.model_dump()})
    try:
        message_id = reaction_role_request.message_id
        reactions = reaction_role_request.reactions

        if not reactions:
            raise HTTPException(
                status_code=400, detail="Reactions list cannot be empty"
            )

        message = await Messages.get_or_none(id=message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        if not message.is_sent:
            raise HTTPException(status_code=400, detail="Message not sent yet")

        guild = await backend.fetch_guild(int(guild_id))
        channel = guild.get_channel(int(message.channel_id))
        if not channel or not isinstance(channel, TextChannel):
            try:
                channel = await guild.fetch_channel(int(message.channel_id))
            except:
                raise HTTPException(status_code=404, detail="Channel not found")

        # Check if the bot has permission to add reactions
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.add_reactions:
            raise HTTPException(
                status_code=403,
                detail="Bot lacks permission to add reactions in this channel",
            )

        # Add only missing reactions to the message
        if not isinstance(channel, TextChannel):
            raise HTTPException(
                status_code=400,
                detail="Selected channel must be a text channel",
            )
        message_discord = await channel.fetch_message(message.message_id)
        # Get current reactions on the message
        current_reactions = set()
        for r in message_discord.reactions:
            if not isinstance(r.emoji, str) and hasattr(r.emoji, "id") and r.emoji.id:
                # Custom emoji
                current_reactions.add(
                    f"<{'a' if getattr(r.emoji, 'animated', False) else ''}:{r.emoji.name}:{r.emoji.id}>"
                )
            else:
                # Unicode emoji
                current_reactions.add(str(r.emoji))

        for reaction in reactions:
            emoji = reaction["emoji"]
            # Support custom emojis from the guild
            emoji_str = emoji
            if isinstance(emoji, str) and emoji.startswith("<") and emoji.endswith(">"):
                match = re.match(r"<a?:\w+:(\d+)>", emoji)
                if match:
                    emoji_id = int(match.group(1))
                    custom_emoji = next(
                        (e for e in guild.emojis if e.id == emoji_id), None
                    )
                    if custom_emoji:
                        emoji_str = f"<{'a' if custom_emoji.animated else ''}:{custom_emoji.name}:{custom_emoji.id}>"
                        if emoji_str not in current_reactions:
                            await message_discord.add_reaction(custom_emoji)
                        continue
            # For unicode emoji
            if emoji_str not in current_reactions:
                await message_discord.add_reaction(emoji)

        # Create or update the reaction roles
        feature = await Feature.get_guild_feature(guild_id, "reaction_roles")
        reaction_roles = feature.get_setting("reaction_roles") or []

        # Check if the message already has reaction roles
        existing_entry = next(
            (entry for entry in reaction_roles if entry["message_id"] == message.id),
            None,
        )
        if existing_entry:
            # Update the existing entry with new data (replace reactions, not extend)
            existing_entry["reactions"] = reactions
            existing_entry["allow_unselect"] = reaction_role_request.allow_unselect
            existing_entry["max_reactions_per_user"] = (
                reaction_role_request.max_reactions_per_user
            )
            existing_entry["require_roles"] = reaction_role_request.require_roles
            existing_entry["forbidden_roles"] = reaction_role_request.forbidden_roles
            existing_entry["cooldown"] = reaction_role_request.cooldown
            existing_entry["remove_reactions"] = reaction_role_request.remove_reactions
        else:
            # Create a new entry for the message
            reaction_roles.append(
                {
                    "message_id": message.id,
                    "channel_id": message.channel_id,
                    "reactions": reactions,
                    "allow_unselect": reaction_role_request.allow_unselect,
                    "max_reactions_per_user": reaction_role_request.max_reactions_per_user,
                    "require_roles": reaction_role_request.require_roles,
                    "forbidden_roles": reaction_role_request.forbidden_roles,
                    "cooldown": reaction_role_request.cooldown,
                    "remove_reactions": reaction_role_request.remove_reactions,
                }
            )

        await feature.set_setting("reaction_roles", reaction_roles)

        return JSONResponse(
            {
                "success": True,
                "message": "Reaction roles created or updated successfully",
            }
        )
    except Exception as e:
        backend.logger.error(f"Error creating reaction roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create reaction roles")


@router.get("/{guild_id}/reaction-roles")
async def get_reaction_roles(
    guild_id: int, request: Request, user: User = Depends(get_user)
):
    """Get all reaction roles for a guild"""
    backend: APIServer = request.app.state.backend
    try:
        feature = await Feature.get_guild_feature(guild_id, "reaction_roles")
        reaction_roles = feature.get_setting("reaction_roles") or []
        return reaction_roles

    except Exception as e:
        backend.logger.error(f"Error fetching reaction roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch reaction roles")


@router.delete("/{guild_id}/reaction-roles/{message_id}")
async def delete_reaction_role(
    guild_id: int, message_id: int, request: Request, user: User = Depends(get_user)
):
    """Delete all reaction roles for a specific message ID and remove the reactions"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Deleted a Reaction Roles", {"message_id": message_id})
    try:
        feature = await Feature.get_guild_feature(guild_id, "reaction_roles")
        reaction_roles = feature.get_setting("reaction_roles") or []

        # Find the message entry
        message_entry = next(
            (entry for entry in reaction_roles if entry["message_id"] == message_id),
            None,
        )

        if message_entry:
            # Remove reactions from the message
            guild = await backend.fetch_guild(int(guild_id))
            channel = guild.get_channel(int(message_entry["channel_id"]))
            if not channel or not isinstance(channel, TextChannel):
                try:
                    channel = await guild.fetch_channel(
                        int(message_entry["channel_id"])
                    )
                except:
                    raise HTTPException(status_code=404, detail="Channel not found")

            # Check if the bot has permission to manage messages
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.manage_messages:
                raise HTTPException(
                    status_code=403,
                    detail="Bot lacks permission to manage messages in this channel",
                )

            if not isinstance(channel, TextChannel):
                raise HTTPException(
                    status_code=400,
                    detail="Selected channel must be a text channel",
                )

            message_discord = await channel.fetch_message(message_entry["message_id"])
            for reaction in message_entry["reactions"]:
                emoji = reaction["emoji"]
                await message_discord.clear_reaction(emoji)

        # Remove the reaction roles entry
        reaction_roles = [rr for rr in reaction_roles if rr["message_id"] != message_id]
        await feature.set_setting("reaction_roles", reaction_roles)

        return JSONResponse(
            {
                "success": True,
                "message": "Reaction roles and reactions deleted successfully",
            }
        )
    except Exception as e:
        backend.logger.error(f"Error deleting reaction role: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete reaction role")


@router.delete("/{guild_id}/reaction-roles/{message_id}/{emoji}")
async def delete_reaction_role_by_emoji(
    guild_id: int,
    message_id: int,
    emoji: str,
    request: Request,
    user: User = Depends(get_user),
):
    """Delete a specific reaction role for a message by emoji and remove the reaction"""
    backend: APIServer = request.app.state.backend
    await Logs.Logger(
            await backend.fetch_guild(guild_id),
            await backend.fetch_user(int(user["id"])),
        ).info("User Deleted a Specifc Emoji Role", {"message_id": message_id, "emoji": emoji})
    try:
        feature = await Feature.get_guild_feature(guild_id, "reaction_roles")
        reaction_roles = feature.get_setting("reaction_roles") or []

        for entry in reaction_roles:
            if entry["message_id"] == message_id:
                entry["reactions"] = [
                    reaction
                    for reaction in entry["reactions"]
                    if reaction["emoji"] != emoji
                ]
                if not entry["reactions"]:
                    reaction_roles.remove(entry)
                break

        # Save updated reaction roles
        await feature.set_setting("reaction_roles", reaction_roles)

        # Remove the reaction from the message
        guild = await backend.fetch_guild(int(guild_id))
        channel = guild.get_channel(int(entry["channel_id"]))
        if not channel or not isinstance(channel, TextChannel):
            try:
                channel = await guild.fetch_channel(int(entry["channel_id"]))
            except:
                raise HTTPException(status_code=404, detail="Channel not found")

        # Check if the bot has permission to manage messages
        permissions = channel.permissions_for(channel.guild.me)
        if not permissions.manage_messages:
            raise HTTPException(
                status_code=403,
                detail="Bot lacks permission to manage messages in this channel",
            )

        if not isinstance(channel, TextChannel):
            raise HTTPException(
                status_code=400,
                detail="Selected channel must be a text channel",
            )

        message_discord = await channel.fetch_message(message_id)
        await message_discord.clear_reaction(emoji)

        return JSONResponse(
            {
                "success": True,
                "message": "Reaction role and reaction deleted successfully",
            }
        )
    except Exception as e:
        backend.logger.error(f"Error deleting reaction role: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete reaction role")


# Getting Logs

@router.get("/{guild_id}/logs")
async def get_logs(
    guild_id: int,
    request: Request,
    user: User = Depends(get_user),
):
    """Get all logs from a speific guild"""
    return list(await Logs.get_logs_by_guild(guild_id))