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
from fastapi import FastAPI, HTTPException
from modules.Nexon import logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from modules.Nexon import overwriteOwner, debug, colours
from modules.settings import FeatureManager

#types string enum
class Types(StrEnum):
    header = "header"
    cards = "cards"
    panel = "panel"


pages: Dict[str, List] = {
    "Overview": [
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
                    "subtext": "Configure AI settings",
                    "icon": "fa-solid fa-robot",
                    "link": "/ai",
                    "buttonText": "Configure AI"
                },
                {
                    "text": "Auto Role",
                    "subtext": "Configure auto role settings",
                    "icon": "fa-solid fa-user-plus" ,
                    "link": "/auto_role",
                    "buttonText": "Configure Auto Role"
                },
                {
                    "text": "Welcome",
                    "subtext": "Configure welcome settings",
                    "icon": "fa-solid fa-gift",
                    "link": "/welcome",
                    "buttonText": "Configure Welcome"
                },
                {
                    "text": "Badges",
                    "subtext": "Configure badge settings",
                    "icon": "fa-solid fa-medal",
                    "link": "/badges",
                    "buttonText": "Configure Badges"
                }
            ]
        }
    ],
    "Basic Settings": [
        {
            "type": Types.header,
            "text": "Basic Settings",
            "subtext": "Basic settings for the server",
            "icon": "fa-solid fa-cog"
        },
        {
            "type": Types.panel,
            "text": "Embed Colour Configuration",
            "icon": "fa-solid fa-palette",
            "subtext": "Configure the embed colour for the server",
            "settings": [
                {
                    "name": "Info Embed Colour",
                    "type": "colour",
                    "value": colours.Info.value
                },
                {
                    "name": "Warning Embed Colour",
                    "type": "colour",
                    "value": colours.Warn.value
                },
                {
                    "name": "Error Embed Colour",
                    "type": "colour",
                    "value": colours.Error.value
                }
            ]
        }
        
    ]
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
        )
        self.npm_command = "npm run dev" if debug else "npm run start"
        
        self.terms_and_services: Optional[str] = None
        self.privacy_policy: Optional[str] = None
        
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
                            "icon": "fa-solid fa-gauge",
                        },
                        {
                            "name": "Basic Settings",
                            "icon": "fa-solid fa-cog"
                        }
                    ],
                    "Features": [
                        {
                            "name": "AI",
                            "icon": "fa-solid fa-robot"
                        },
                        {
                            "name": "Auto Role",
                            "icon": "fa-solid fa-user-plus"
                        },
                        {
                            "name": "Backup",
                            "icon": "fa-solid fa-hdd"
                        },
                        {
                            "name": "Custom Roles",
                            "icon": "fa-solid fa-user-tag"
                        },
                        {
                            "name": "Temporary Voice",
                            "icon": "fa-solid fa-headset"
                        },
                        {
                            "name": "Welcome",
                            "icon": "fa-solid fa-gift"
                        },
                        {
                            "name": "Leveling",
                            "icon": "fa-solid fa-trophy"
                        },
                        {
                            "name": "Badges",
                            "icon": "fa-solid fa-medal"
                        }
                    ]
                }
        @self.app.get("/api/layout/settings/server/{page}")
        async def get_server_settings_page(page: str):
            """Get server settings page"""
            return pages[page]

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
        
        
        # Admin
        @self.app.post("/api/admin/is_owner")
        async def is_owner(request: OwnerCheckRequest):
            """Check if a user is the bot owner"""
            try:
                user_id = int(request.user_id)
                is_owner = user_id == overwriteOwner or user_id == self.bot.owner_id
                return {"is_owner": is_owner}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user ID")
        
        @self.app.post("/api/admin/create_badge")
        async def create_badge(request: CreateBadgeRequest):
            """Create a new badge"""
            try:
                # Convert dictionary requirements to BadgeRequirement objects
                
                payload = Badge(
                    name=request.name,
                    description=request.description,
                    icon_url=request.icon_url,
                    rarity=Rarity(request.rarity),
                    requirements=request.requirements,
                    hidden=request.hidden
                )
                await BadgeManager().add_badge(payload)
                return {"success": True}
            except Exception as e:
                self.logger.error(f"Error creating badge: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
        
        
        #Other
        @self.app.get("/api/terms_and_services")
        async def get_terms_and_services():
            """Get terms and services"""
            if not self.terms_and_services:
                return self.terms_and_services
            else:
                with open("Terms of Service.md", "r") as file:
                    self.terms_and_services = file.read()
                return self.terms_and_services
        @self.app.get("/api/privacy_policy")
        async def get_privacy_policy():
            """Get privacy policy"""
            if not self.privacy_policy:
                return self.privacy_policy
            else:
                with open("Privacy Policy.md", "r") as file:
                    self.privacy_policy = file.read()
                return self.privacy_policy
            
        
    async def start_dashboard(self):
        """Start the dashboard"""
        self.logger.info("Starting web dashboard...")

        # Start npm process
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
            await asyncio.gather(
                self.server.serve(),
                self.npm_process.communicate()
            )
            self.logger.info("Web dashboard started successfully")
        except Exception as e:
            self.logger.error(f"Error starting dashboard: {e}")
            if self.npm_process and self.npm_process.returncode is None:
                self.npm_process.terminate()
            raise

    @commands.Cog.listener()
    async def on_ready(self):
        asyncio.create_task(self.start_dashboard())

    def cog_unload(self):
        if self.npm_process and self.npm_process.returncode is None:
            self.npm_process.terminate()

def setup(client):
    client.add_cog(DashboardCog(client))