from datetime import datetime
from enum import StrEnum
import platform
from typing import Dict, List, Optional, Union
from nexon import IntegrationType, SlashApplicationCommand, UserApplicationCommand, MessageApplicationCommand
from nexon.ext import commands
from nexon.badge import Badge, BadgeManager
from nexon.enums import RequirementType, Rarity, ComparisonType
import asyncio
import psutil
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from modules.Nexon import logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from modules.Nexon import overwriteOwner, debug, colours, config, split_frontend
from modules.settings import FeatureManager
import requests
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from aiohttp import ClientSession, ClientTimeout
import time
from typing import Dict, List, Optional, Union, Any

#types string enum
class Types(StrEnum):
    header = "header"
    cards = "cards"
    panel = "panel"


pages: Dict[str, List] = {
    "overview": [
        {
            "type": Types.header,
            "text": "Overview",
            "subtext": "General information about the server",
            "icon": "fa-solid fa-gauge" 
        },
        {
            "type": Types.cards,
            "interaction": "link_button",
            "buttons": [
                {
                    "text": "AI",
                    "subtext": "Configure AI settings and responses",
                    "icon": "fa-solid fa-robot",
                    "link": "/ai",
                    "buttonText": "Configure AI"
                },
                {
                    "text": "Auto Role",
                    "subtext": "Manage automatic role assignment",
                    "icon": "fa-solid fa-user-plus",
                    "link": "/auto_role",
                    "buttonText": "Configure Auto Role"
                },
                {
                    "text": "Welcome",
                    "subtext": "Customize welcome messages and images",
                    "icon": "fa-solid fa-gift",
                    "link": "/welcome", 
                    "buttonText": "Configure Welcome"
                },
                {
                    "text": "Badges",
                    "subtext": "Manage achievement badges",
                    "icon": "fa-solid fa-medal",
                    "link": "/badges",
                    "buttonText": "Configure Badges"
                },
                {
                    "text": "Leveling",
                    "subtext": "Configure XP and level settings",
                    "icon": "fa-solid fa-trophy",
                    "link": "/leveling",
                    "buttonText": "Configure Leveling"
                },
                {
                    "text": "Temp Channels",
                    "subtext": "Manage temporary voice channels",
                    "icon": "fa-solid fa-headset",
                    "link": "/temp-voice",
                    "buttonText": "Configure Temp Channels"
                }
            ]
        }
    ],
    "basic-settings": [
        {
            "type": Types.header,
            "text": "Basic Settings",
            "subtext": "Core server configuration",
            "icon": "fa-solid fa-cog"
        },
        {
            "type": Types.panel,
            "text": "Embed Appearance",
            "icon": "fa-solid fa-palette",
            "subtext": "Customize bot message appearances",
            "settings": [
                {
                    "name": "Info Embed Color",
                    "type": "color",
                    "value": colours.Info.hex,
                    "description": "Color for informational messages"
                },
                {
                    "name": "Warning Embed Color",
                    "type": "color", 
                    "value": colours.Warn.hex,
                    "description": "Color for warning messages"
                },
                {
                    "name": "Error Embed Color",
                    "type": "color",
                    "value": colours.Error.hex,
                    "description": "Color for error messages"
                }
            ]
        },
        {
            "type": Types.panel,
            "text": "Badge Appearance",
            "icon": "fa-solid fa-medal",
            "subtext": "Customize badge appearances",
            "settings": [
                {
                    "name": "Badge Common Color",
                    "type": "color",
                    "value": colours.Common.hex,
                    "description": "Color for success messages"
                },
                {
                    "name": "Badge Uncommon Color",
                    "type": "color",
                    "value": colours.Uncommon.hex,
                    "description": "Color for uncommon badges"
                },
                {
                    "name": "Badge Rare Color",
                    "type": "color",
                    "value": colours.Rare.hex,
                    "description": "Color for rare badges"
                },
                {
                    "name": "Badge Epic Color",
                    "type": "color",
                    "value": colours.Epic.hex,
                    "description": "Color for epic badges"
                },
                {
                    "name": "Badge Legendary Color",
                    "type": "color",
                    "value": colours.Legendary.hex,
                    "description": "Color for legendary badges"
                }
            ]
        }
    ],
}

class OwnerCheckRequest(BaseModel):
    user_id: str

class BadgeRequirement(BaseModel):
    type: str
    value: int
    comparison: str
    specific_value: str = ""

class CreateBadgeRequest(BaseModel):
    name: str
    description: str
    icon_url: str
    rarity: int = Field(ge=1, le=5)
    requirements: List[Dict[str, Union[str, int]]]
    hidden: bool = False

class GuildsRequest(BaseModel):
    guilds: List[str]

class FeatureSetRequest(BaseModel):
    feature_name: str
    value: Union[str, bool, int, float]

class DiscordCallbackRequest(BaseModel):
    code: str

class DashboardCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client
        self.app = FastAPI(
            title="Bot Dashboard API",
            description="API for bot dashboard",
            version="1.0.0"
        )
        self.startTime = datetime.now()
        self.logger = logger
        self.npm_process = None
        self.server = None
        self.commands: Optional[List[Dict[str,str]]] = None
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://negomi.mahirou.online", "http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"]
        )
        self.npm_command = "npm run dev" if debug else "npm run start"
        
        self.terms_and_services: Optional[str] = None
        self.privacy_policy: Optional[str] = None
        
        # Add caches
        self.token_cache = TTLCache(maxsize=1000, ttl=3600)
        self.user_cache = TTLCache(maxsize=1000, ttl=300)
        self.guild_cache = TTLCache(maxsize=1000, ttl=300)
        self.rate_limits: Dict[str, float] = {}
        self.session: Optional[ClientSession] = None
        # Add invite URL cache
        self.invite_url_cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes cache
        
        self.setup_routes()
    
    def get_commands_func(self):
        if not self.commands:
            commands = []
            for command in self.bot.get_application_commands():
                if command.integration_types:
                    guild_installed = IntegrationType.guild_install in command.integration_types
                    user_installed = IntegrationType.user_install in command.integration_types
                else:
                    guild_installed = True
                    user_installed = False
                try:
                    base_data = {
                        "name": "",
                        "description": "",
                        "usage": "",
                        "type": "",
                        "category": command.parent_cog.__class__.__name__ if command.parent_cog else "No Category",
                        "admin_only": getattr(command, 'default_member_permissions', None) is not None 
                            and command.default_member_permissions.administrator, # type: ignore
                        "guild_only": getattr(command, 'guild_only', False),
                        "guild_installed": guild_installed,  # Add logic if needed
                        "user_installed": user_installed,   # Add logic if needed
                        "permissions": [],
                        "cooldown": getattr(command, 'cooldown', None),
                        "examples": getattr(command, 'examples', [])
                    }

                    if isinstance(command, UserApplicationCommand):
                        command_data = {
                            **base_data,
                            "name": command.name,
                            "description": command.description or "User context command",
                            "usage": f"Right-click user → Apps → {command.name}",
                            "type": "member",
                        }
                        commands.append(command_data)
                        continue
                    
                    if isinstance(command, MessageApplicationCommand):
                        command_data = {
                            **base_data,
                            "name": command.name,
                            "description": command.description or "Message context command",
                            "usage": f"Right-click message → Apps → {command.name}",
                            "type": "message",
                        }
                        commands.append(command_data)
                        continue

                    if isinstance(command, SlashApplicationCommand):
                        if command.children:
                            self._process_subcommands(command, commands, base_data)
                            continue

                        options = self._get_command_options(command)
                        command_data = {
                            **base_data,
                            "name": command.name,
                            "description": command.description,
                            "usage": f"/{command.name} " + " ".join(f"[{opt}]" for opt in options),
                            "type": "slash",
                        }
                        commands.append(command_data)

                except Exception as e:
                    self.logger.error(f"Error processing command {command.name}: {str(e)}")
                    
            self.commands = commands
        return self.commands

    def _get_command_options(self, command):
        options = []
        for option in command.options:
            if isinstance(option, str):
                options.append(option)
            elif hasattr(option, 'name'):
                option_type = getattr(option, 'type', 'value')
                options.append(f"{option.name}:{option_type}")
            else:
                options.append(str(option))
        return options

    def _process_subcommands(self, command, commands_list, base_data, parent_name=""):
        for child_name, child in command.children.items():
            # Build the command name by properly joining all parts
            if parent_name:
                current_name = f"{parent_name} {child_name}"
                full_command_name = f"{command.name} {parent_name} {child_name}"
            else:
                current_name = child_name
                full_command_name = f"{command.name} {child_name}"
            
            if child.children:
                self._process_subcommands(child, commands_list, base_data, current_name)
            else:
                options = self._get_command_options(child)
                command_data = {
                    **base_data,
                    "name": full_command_name,
                    "description": child.description,
                    "usage": f"/{full_command_name} " + " ".join(f"[{opt}]" for opt in options),
                    "type": "slash",
                }
                commands_list.append(command_data)
    async def get_guild(self, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(guild_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Guild not found")
        return guild

    async def get_session(self) -> ClientSession:
        if self.session is None or self.session.closed:
            self.session = ClientSession(timeout=ClientTimeout(total=10))
        return self.session

    async def rate_limited_request(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """Make a rate-limited request to Discord API"""
        now = time.time()
        key = f"{method}:{endpoint}"
        
        # Check rate limit
        if key in self.rate_limits:
            time_passed = now - self.rate_limits[key]
            if time_passed < 0.5:  # Minimum 500ms between requests
                await asyncio.sleep(0.5 - time_passed)
        
        self.rate_limits[key] = now
        
        session = await self.get_session()
        async with session.request(method, f"https://discord.com/api/v10{endpoint}", **kwargs) as resp:
            if resp.status == 429:
                retry_after = float(resp.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after)
                return await self.rate_limited_request(endpoint, method, **kwargs)
            return await resp.json()

    async def verify_auth(self, request: Request) -> Optional[str]:
        """Verify authentication and return access token if valid"""
        access_token = request.cookies.get("accessToken")
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Verify token is valid by checking user cache or making a test request
        if access_token not in self.user_cache:
            try:
                user = await self.rate_limited_request(
                    "/users/@me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                self.user_cache[access_token] = user
            except Exception as e:
                raise HTTPException(status_code=401, detail="Invalid token")
                
        return access_token

    def setup_routes(self):
        
        # Bot
        @self.app.get("/api/commands")
        async def get_commands():
            """Get all bot commands"""
            return {"commands": self.get_commands_func()}

        @self.app.get("/api/stats")
        async def get_stats():
            """Get detailed bot and system statistics"""
            process = psutil.Process()
            return {
                "system": {
                    "cpu_usage": round(psutil.cpu_percent(), 2),
                    "memory_usage": round(process.memory_percent(), 2),
                    "memory_total": psutil.virtual_memory().total,
                    "python_version": platform.python_version(),
                    "os": f"{platform.system()} {platform.release()}",
                    "uptime": round(process.create_time(), 2),
                    "thread_count": process.num_threads(),
                    "disk_usage": round(psutil.disk_usage('/').percent, 2)
                },
                "bot": {
                    "guild_count": len(self.bot.guilds),
                    "user_count": sum(g.member_count or 0 for g in self.bot.guilds),
                    "channel_count": sum(len(g.channels) for g in self.bot.guilds),
                    "voice_connections": len(self.bot.voice_clients),
                    "latency": round(self.bot.latency * 1000),
                    "uptime": (datetime.now() - self.startTime).total_seconds(),
                    "command_count": len(self.get_commands_func()),
                    "cogs_loaded": len(self.bot.cogs),
                    "current_shard": getattr(self.bot, "shard_id", 0),
                    "messages_sent": 0,
                    "commands_processed": 0,
                    "errors_encountered": 0,
                    "shard_count": self.bot.shard_count or 1,
                },
                "timestamp": datetime.now().timestamp()
            }
        
        # Guilds
        @self.app.get("/api/guilds")
        async def get_guilds():
            """Get summary of all guilds"""
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
                    } for guild in self.bot.guilds
                ]
            }

        @self.app.get("/api/guilds/{guild_id}")
        async def get_guild(guild_id: int):
            """Get detailed information about a specific guild"""
            guild = await self.get_guild(guild_id)
            
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
        @self.app.post("/api/guilds/{guild_id}/is_admin")
        async def is_admin(guild_id: int, request: Request):
            """Check if the user is an admin in the guild"""
            try:
                access_token = await self.verify_auth(request)
                
                # Get user from cache or API
                if access_token in self.user_cache:
                    user = self.user_cache[access_token]
                else:
                    user = await self.rate_limited_request(
                        "/users/@me",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    self.user_cache[access_token] = user

                # Get guild
                guild = await self.get_guild(guild_id)
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
                self.logger.error(f"Error checking admin status: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "isAdmin": False,
                        "detail": "An internal server error occurred. Please try again later."
                    }
                )
        
        @self.app.get("/api/guilds/{guild_id}/channels_names")
        async def get_guild_channels_names(guild_id: int):
            """Get channel names for a specific guild"""
            guild = await self.get_guild(guild_id)
            
            return [channel.name for channel in guild.channels]
        @self.app.get("/api/guilds/{guild_id}/channels")
        async def get_guild_channels(guild_id: int):
            """Get channels for a specific guild"""
            guild = await self.get_guild(guild_id)
            
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
        
        @self.app.get("/api/guilds/{guild_id}/joined")
        async def get_joined_guilds(guild_id: int) -> bool:
            """Check if the bot is in a specific guild"""
            return guild_id in [g.id for g in self.bot.guilds]
        

        @self.app.post("/api/guilds/filter_joined")
        async def filter_joined_guilds(request: GuildsRequest) -> List[str]:
            """Return list of guild IDs that the bot is a member of"""
            return [guild for guild in request.guilds if int(guild) in [g.id for g in self.bot.guilds]]
            
        # [GET] /api/layout/settings/sidebar
        # [GET] /api/layout/settings/{page}
        # [GET] /api/layout/settings/server/{page}
        
        @self.app.get("/api/layout/settings/sidebar")
        async def get_sidebar():
            """Get sidebar settings"""
            return {
                    "General": [
                        {
                            "name": "Overview",
                            "icon": "fa-solid fa-gauge",
                        },
                        {
                            "name": "Basic Settings",
                            "icon": "fa-solid fa-cog",
                        },
                        {
                            "name": "Badges",
                            "icon": "fa-solid fa"
                        }
                    ]
                    # React Adds another Section of Servers
            }
        
        @self.app.get("/api/layout/settings/server/sidebar")
        async def get_server_sidebar():
            """Get server sidebar settings"""
            return {
                    "General": [
                        {
                            "name": "Overview",
                            "link": "overview",
                            "icon": "fa-solid fa-gauge",
                        },
                        {
                            "name": "Basic Settings",
                            "link": "basic-settings",
                            "icon": "fa-solid fa-cog"
                        }
                    ],
                    "Features": [
                        {
                            "name": "AI",
                            "link": "ai",
                            "icon": "fa-solid fa-robot"
                        },
                        {
                            "name": "Auto Role",
                            "link": "auto-role",
                            "icon": "fa-solid fa-user-plus"
                        },
                        {
                            "name": "Backup",
                            "link": "backup",
                            "icon": "fa-solid fa-hdd"
                        },
                        {
                            "name": "Custom Roles",
                            "link": "custom-roles",
                            "icon": "fa-solid fa-user-tag"
                        },
                        {
                            "name": "Temporary Voice",
                            "link": "temp-voice",
                            "icon": "fa-solid fa-headset"
                        },
                        {
                            "name": "Welcome",
                            "link": "welcome",
                            "icon": "fa-solid fa-gift"
                        },
                        {
                            "name": "Leveling",
                            "link": "leveling",
                            "icon": "fa-solid fa-trophy"
                        },
                        {
                            "name": "Badges",
                            "link": "badges",
                            "icon": "fa-solid fa-medal"
                        }
                    ]
                }
        @self.app.get("/api/layout/settings/server/{page}")
        async def get_server_settings_page(page: str):
            """Get server settings page"""
            return pages[page]

        @self.app.get("/api/guilds/{guild_id}/settings/{page}")
        async def get_settings(guild_id: int, page: str):
            """Get saved settings for a specific page"""
            try:
                featureManager = FeatureManager(guild_id, page.replace("%20", " "))
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
                                self.logger.info(f"Loading setting {setting['name']}: {settings[setting['name']]} (saved: {saved_value}, default: {setting['value']})")
                
                return {"settings": settings}
            except Exception as e:
                self.logger.error(f"Error getting settings: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.post("/api/guilds/{guild_id}/settings/{page}")
        async def save_settings(guild_id: int, page: str, request: Request):
            """Save all settings for a specific page"""
            try:
                data = await request.json()
                settings = data.get("settings", {})
                featureManager = FeatureManager(guild_id, page)
                
                for setting_name, value in settings.items():
                    featureManager.set_setting(setting_name, value)
                
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error saving settings: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/api/guilds/{guild_id}/settings/{page}")
        async def delete_settings(guild_id: int, page: str):
            """Delete all settings for a specific page"""
            try:
                FeatureManager(guild_id, page).delete_class()
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error deleting settings: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

        # Features
        
        @self.app.post("/api/guild/{guild_id}/features/{class_name}/set")
        async def set_feature(guild_id: int, class_name: str, request: FeatureSetRequest):
            """Set a feature for a specific guild"""
            featureManager = FeatureManager(guild_id, class_name)
            featureManager.set_setting(request.feature_name, request.value)
            return {"success": True}
        @self.app.get("/api/guild/{guild_id}/features/{class_name}/get")
        async def get_feature(guild_id: int, class_name: str, feature_name: str):
            """Get a feature for a specific guild"""
            featureManager = FeatureManager(guild_id, class_name)
            return {feature_name: featureManager.get_setting(feature_name)}
        @self.app.post("/api/guild/{guild_id}/features/{class_name}/reset")
        async def reset_feature(guild_id: int, class_name: str, feature_name: str):
            """Reset a feature for a specific guild"""
            featureManager = FeatureManager(guild_id, class_name)
            if featureManager.delete_setting(feature_name):
                return {"success": True}
            else:
                raise HTTPException(status_code=404, detail="Feature not found")
        
        @self.app.post("/api/guild/{guild_id}/features/{class_name}/enable")
        async def enable_feature(guild_id: int, class_name: str):
            """Enable a class for a specific guild"""
            featureManager = FeatureManager(guild_id, class_name)
            if featureManager.is_disabled():
                featureManager.enable_class()
                return {"success": True}
            else:
                raise HTTPException(status_code=400, detail="Feature already enabled")
        @self.app.post("/api/guild/{guild_id}/features/{class_name}/disable")
        async def disable_feature(guild_id: int, class_name: str):
            """Disable a class for a specific guild"""
            featureManager = FeatureManager(guild_id, class_name)
            if featureManager.is_enabled():
                featureManager.disable_class()
                return {"success": True}
            else:
                raise HTTPException(status_code=400, detail="Feature already disabled")
        @self.app.get("/api/guild/{guild_id}/features/{class_name}/status")
        async def get_feature_status(guild_id: int, class_name: str):
            return {"enabled": FeatureManager(guild_id, class_name).is_enabled()}       
        
        @self.app.get("/api/admin/is_owner")
        async def is_owner(request: Request):
            """Check if the authenticated user is the bot owner"""
            try:
                # Verify authentication and get access token
                access_token = await self.verify_auth(request)
                
                # Get user from cache or Discord API
                if access_token in self.user_cache:
                    user = self.user_cache[access_token]
                else:
                    user = await self.rate_limited_request(
                        "/users/@me",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    self.user_cache[access_token] = user
                
                # Check if user is owner
                user_id = int(user["id"])
                is_owner = user_id == overwriteOwner or user_id == self.bot.owner_id
                
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
                self.logger.error(f"Error checking owner status: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )
            
        @self.app.post("/api/admin/stats")
        async def get_admin_stats():
            """Get detailed bot statistics for admin"""
            try:
                # Get total badges
                badge_manager = BadgeManager()
                badges = await badge_manager.get_all_badges()
                total_badges = len(badges)

                # Get total servers
                total_servers = len(self.bot.guilds)

                # Calculate active users (unique users across all guilds)
                active_users = set()
                for guild in self.bot.guilds:
                    for member in guild.members:
                        active_users.add(member.id)

                return {
                    "total_badges": total_badges,
                    "total_servers": total_servers,
                    "active_users": len(active_users)
                }

            except Exception as e:
                self.logger.error(f"Error getting admin stats: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        async def check_owner(request: Request):
            access_token = await self.verify_auth(request)
            if access_token in self.user_cache:
                user = self.user_cache[access_token]
            else:
                user = await self.rate_limited_request(
                    "/users/@me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                self.user_cache[access_token] = user
            user_id = int(user["id"])
            if user_id != overwriteOwner and user_id != self.bot.owner_id:
                raise HTTPException(status_code=403, detail="Not authorized")

        @self.app.post("/api/admin/badges/create")
        async def create_badge(request: Request, badge_request: CreateBadgeRequest):
            """Create a new badge"""
            try:
                # Convert dictionary requirements to BadgeRequirement objects
                await check_owner(request)
                
                requirements = [
                    {
                        "type": req["type"],
                        "value": req["value"], 
                        "comparison": str(ComparisonType(req["comparison"])),
                        "specific_value": req.get("specific_value", "")
                    } for req in badge_request.requirements
                ]
                payload = Badge(
                    name=badge_request.name,
                    description=badge_request.description,
                    icon_url=badge_request.icon_url,
                    rarity=Rarity(badge_request.rarity),
                    requirements=badge_request.requirements,
                    hidden=badge_request.hidden
                )
                await BadgeManager().add_badge(payload)
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error creating badge: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/admin/badges")
        async def get_badges():
            """Get all badges"""
            try:
                badges = await BadgeManager().get_all_badges()
                return {"badges": [badge.to_dict() for badge in badges]}
            except Exception as e:
                self.logger.error(f"Error fetching badges: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/admin/badges/{badge_id}/edit")
        async def edit_badge(badge_id: int,request: Request, request_badge: CreateBadgeRequest):
            """Edit an existing badge"""
            try:
                await check_owner(request)
                # Convert dictionary requirements to BadgeRequirement objects
                requirements = [
                    {
                        "type": req["type"],
                        "value": req["value"],
                        "comparison": str(ComparisonType(req["comparison"])),
                        "specific_value": req.get("specific_value", "")
                    } for req in request_badge.requirements
                ]
                
                badge = Badge(
                    name=request_badge.name,
                    description=request_badge.description,
                    icon_url=request_badge.icon_url,
                    rarity=Rarity(request_badge.rarity),
                    requirements=requirements,
                    hidden=request_badge.hidden
                )
                
                await BadgeManager().update_badge(badge_id, badge)
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error editing badge: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        @self.app.post("/api/admin/badges/{badge_id}/delete")
        async def delete_badge(badge_id: int, request: Request):
            """Delete a badge"""
            try:
                await check_owner(request)
                await BadgeManager().remove_badge(badge_id)
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error deleting badge: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        @self.app.get("/api/admin/badges/{badge_id}")
        async def get_badge(badge_id: int):
            """Get detailed information about a specific badge"""
            try:
                badge = await BadgeManager().get_badge(badge_id)
                if not badge:
                    raise HTTPException(status_code=404, detail="Badge not found")
                return badge.to_dict()
            except Exception as e:
                self.logger.error(f"Error fetching badge: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
            
        
        
        #Other
        @self.app.get("/api/terms-and-service")
        async def get_terms_and_services():
            """Get terms and services"""
            if self.terms_and_services:
                return self.terms_and_services
            else:
                with open("Terms of Service.md", "r") as file:
                    self.terms_and_services = file.read()
                return self.terms_and_services
        @self.app.get("/api/privacy-policy")
        async def get_privacy_policy():
            """Get privacy policy"""
            if self.privacy_policy:
                return self.privacy_policy
            else:
                with open("Privacy Policy.md", "r") as file:
                    self.privacy_policy = file.read()
                return self.privacy_policy

        @self.app.post("/api/auth/discord/callback")
        async def discord_callback(request: DiscordCallbackRequest):
            try:
                code = request.code
                
                # Check cache first
                if code in self.token_cache:
                    return JSONResponse(self.token_cache[code])
                
                data = {
                    "client_id": config.oauth.client_id,
                    "client_secret": config.oauth.client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": config.oauth.redirect_url if not debug else config.oauth.debug_redirect_url,
                }
                
                session = await self.get_session()
                async with session.post(
                    "https://discord.com/api/oauth2/token",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Discord auth failed: {error_data.get('error_description', 'Unknown error')}"
                        )
                    
                    tokens = await response.json()
                    access_token = tokens["access_token"]
                    
                    # Get user data
                    user = await self.rate_limited_request(
                        "/users/@me",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    
                    response_data = {
                        "user": user,
                        "accessToken": access_token
                    }
                    
                    # Cache the response
                    self.token_cache[code] = response_data
                    self.user_cache[access_token] = user
                    
                    return JSONResponse(response_data)
                    
            except Exception as e:
                self.logger.error(f"Discord callback error: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.get("/api/auth/user")
        async def get_user(request: Request):
            """Get authenticated user data"""
            try:
                access_token = await self.verify_auth(request)
                
                # Return cached user data if available
                if access_token in self.user_cache:
                    return {"user": self.user_cache[access_token]}
                
                # Should never reach here due to verify_auth, but just in case
                raise HTTPException(status_code=401, detail="Not authenticated")
                
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": str(e.detail)}
                )

        @self.app.get("/api/auth/user/guilds")
        async def get_user_guilds(request: Request):
            """Get user's guilds"""
            try:
                access_token = await self.verify_auth(request)
                
                session = await self.get_session()
                async with session.get(
                    "https://discord.com/api/users/@me/guilds",
                    headers={"Authorization": f"Bearer {access_token}"}
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Failed to fetch guild information"
                        )
                        
                    guilds = await response.json()
                    return {"guilds": guilds}
                    
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": str(e.detail)}
                )

        @self.app.get("/api/auth/discord/login")
        async def get_discord_login(guild_id: Optional[str] = None):
            """Get Discord OAuth2 login URL"""
            SCOPES = ["identify", "email", "guilds"]
            
            base_url = "https://discord.com/api/oauth2/authorize"
            params = {
                "client_id": config.oauth.client_id,
                "redirect_uri": config.oauth.redirect_url if not debug else config.oauth.debug_redirect_url,
                "response_type": "code",
                "scope": " ".join(SCOPES)
            }
            
            if guild_id:
                params["guild_id"] = guild_id
            
            auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
            return JSONResponse(
                {"message": "Redirecting to Discord OAuth2"},
                headers={"Location": auth_url},
                status_code=307
            )
        @self.app.post("/api/auth/discord/logout")
        async def logout(request: Request):
            """Log out user from Discord"""
            try:
                access_token = request.cookies.get("accessToken")
                if not access_token:
                    return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

                session = await self.get_session()
                async with session.post(
                    "https://discord.com/api/oauth2/token/revoke",
                    data={
                        "token": access_token,
                        "client_id": config.oauth.client_id,
                        "client_secret": config.oauth.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    if response.status != 200:
                        self.logger.error(f"Failed to revoke token: {await response.text()}")

                # Clear caches regardless of revoke success
                if access_token in self.user_cache:
                    del self.user_cache[access_token]

                response = JSONResponse({"success": True})
                response.delete_cookie("accessToken")
                response.delete_cookie("user_id")
                return response

            except Exception as e:
                self.logger.error(f"Logout error: {str(e)}")
                return JSONResponse({"success": False, "error": str(e)})
        
        @self.app.get("/api/auth/bot/invite")
        async def get_bot_invite(guild_id: Optional[str] = None):
            """Get bot invite URL with rate limiting and caching"""
            cache_key = f"invite_url_{guild_id}" if guild_id else "invite_url_default"
            
            # Check cache
            if cache_key in self.invite_url_cache:
                return {"url": self.invite_url_cache[cache_key]}
            
            # Generate invite URL
            SCOPES = ["bot", "applications.commands"]
            PERMISSIONS = "8"  # Administrator permissions
            
            params = {
                "client_id": config.oauth.client_id,
                "permissions": PERMISSIONS,
                "scope": " ".join(SCOPES)
            }
            
            if guild_id:
                params["guild_id"] = guild_id
                
            url = f"https://discord.com/api/oauth2/authorize?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            
            # Cache the URL
            self.invite_url_cache[cache_key] = url
            
            return JSONResponse(
                {"message": "Redirecting to bot invite URL"},
                headers={"Location": url},
                status_code=307
            )
        
        @self.app.get("/api/owner_pfp_url")
        async def get_owner_pfp_url():
            """Get the bot owner's profile picture URL"""
            try:
                ownerID = overwriteOwner or self.bot.owner_id
                if not isinstance(ownerID, int):
                    return {"url": None}
                owner = self.bot.get_user(ownerID)
                if not owner:
                    owner = await self.bot.fetch_user(ownerID)
                if owner.avatar:
                    return {"url": str(owner.avatar.url)}
                else:
                    return {"url": None}
            except Exception as e:
                self.logger.error(f"Error fetching owner's profile picture: {str(e)}")
                return {"url": None}
        
        
    async def _handle_npm_output(self, stream, prefix):
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded_line = line.decode().strip()
            if "Warning" in decoded_line:
                self.logger.warning(f"[NPM] {decoded_line}")
            elif "[ERROR]" in decoded_line:
                self.logger.error(f"[NPM] {decoded_line}")
            elif debug:
                self.logger.info(f"[NPM] {decoded_line}")

    async def start_dashboard(self):
        """Start the dashboard"""
        self.logger.info("Starting web dashboard...")

        # Start npm process
        if not split_frontend:
            self.npm_process = await asyncio.create_subprocess_shell(
                f"cd Dashboard && {self.npm_command}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        # Start FastAPI server
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=25400,
            log_config=None
        )
        self.server = uvicorn.Server(config)
        
        try:
            self.logger.info("Web dashboard started successfully")
            if not split_frontend and self.npm_process:
                self.logger.info("NPM process started successfully")
                await asyncio.gather(
                    self.server.serve(),
                    self._handle_npm_output(self.npm_process.stdout, "stdout"),
                    self._handle_npm_output(self.npm_process.stderr, "stderr")
                )
            else:
                await self.server.serve()
        except Exception as e:
            self.logger.error(f"Error starting dashboard: {e}")
            if self.npm_process and self.npm_process.returncode is None and not split_frontend:
                self.npm_process.terminate()
            raise

    async def cleanup(self):
        if self.session and not self.session.closed:
            await self.session.close()

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.start_dashboard())

    def cog_unload(self):
        if self.npm_process and self.npm_process.returncode is None:
            self.npm_process.terminate()
        asyncio.create_task(self.cleanup())

def setup(client):
    client.add_cog(DashboardCog(client))