import asyncio
from datetime import datetime
from nextcord.ext import ipc
from nextcord.ext.commands import Bot
from nextcord import UserApplicationCommand, SlashApplicationCommand, ForumChannel, BaseApplicationCommand
from typing import Callable, Dict, List, Optional, Any
from threading import Thread
import psutil
import platform
import os
from .Users import load_json_files, analyze_data, UserManager, BotStatistics
from .config import BotConfig
from .logger import logger

class IPCManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logger
        self.routes: Dict[str, Callable] = {}
        self.server = ipc.Server(
            bot=self.bot,
            do_multicast=False
        )
        self.commands: Optional[List[Dict[str,str]]] = None
        
    def route(self, name: str):
        """Decorator to register an IPC route"""
        def decorator(func: Callable):
            self.routes[name] = func
            @self.server.route(name)
            async def wrapped_route(data):
                try:
                    return await func(data)
                except Exception as e:
                    self.logger.error(f"IPC route {name} error: {str(e)}")
                    return {"error": str(e)}
            return wrapped_route
        return decorator

    def setup_default_routes(self):
        """Setup default IPC routes"""
        @self.route("get_guild")
        async def get_guild(data):
            guild = self.bot.get_guild(data.get("guild_id"))
            return guild.to_dict() if guild else None

        @self.route("get_guilds")
        async def get_guilds(_):
            return [g.to_dict() for g in self.bot.guilds]

        @self.route("get_guild_count")
        async def get_guild_count(_):
            return len(self.bot.guilds)
        @self.route("get_icon")
        async def get_icon(_):
            return self.bot.user.display_avatar.url

        @self.route("get_bot_stats")
        async def get_bot_stats(_):
            return {
                "guild_count": len(self.bot.guilds),
                "user_count": sum(g.member_count for g in self.bot.guilds),
                "ping": round(self.bot.latency * 1000),
                "uptime": (datetime.now() - self.bot.start_time).total_seconds()
            }
        @self.route("get_commands")
        async def get_commands(_):
            return get_commands_func()

        def get_commands_func(_: Optional[Any]):
            if not self.commands:
                commands = []
                for command in self.bot.get_application_commands():
                    try:
                        required_permissions = []
                        try:
                            if hasattr(command, 'default_member_permissions'):
                                admin_only = command.default_member_permissions.administrator
                            else:
                                admin_only = False
                        except:
                            admin_only = False

                        
                        # Base command data
                        base_data = {
                            "admin_only": admin_only,
                            "permissions": list(set(required_permissions)),
                            "guild_only": getattr(command, 'guild_only', False),
                            "cooldown": getattr(command, 'cooldown', None),
                            "category": command.parent_cog.__class__.__name__ if command.parent_cog else "No Category",
                        }

                        if isinstance(command, UserApplicationCommand):
                            commandJson = {
                                **base_data,
                                "name": command.name,
                                "description": command.description or "User context command",
                                "usage": f"Right-click user → Apps → {command.name}",
                                "type": "user",
                                "examples": getattr(command, 'examples', []),
                            }
                            commands.append(commandJson)
                            continue

                        if isinstance(command, SlashApplicationCommand):
                            # Handle regular slash commands
                            if command.children:
                                # Recursively process subcommands
                                def process_subcommands(cmd, parent_name=""):
                                    subcmds = []
                                    for child_name, child in cmd.children.items():
                                        full_name = f"{parent_name} {child_name}" if parent_name else child_name
                                        if child.children:
                                            subcmds.extend(process_subcommands(child, f"{full_name}"))
                                        else:
                                            options = []
                                            for option in child.options:
                                                if hasattr(option, 'name'):
                                                    option_type = getattr(option, 'type', 'value')
                                                    options.append(f"{option.name}:{option_type}")
                                                else:
                                                    options.append(str(option))
                                            
                                            subcmds.append({
                                                **base_data,
                                                "name": f"{command.name} {full_name}",
                                                "description": child.description,
                                                "usage": f"/{command.name} {full_name} " + " ".join([f"[{opt}]" for opt in options]),
                                                "type": "slash",
                                                "examples": getattr(child, 'examples', []),
                                            })
                                    return subcmds
                                
                                commands.extend(process_subcommands(command))
                                continue
                                
                            options = []
                            for option in command.options:
                                if hasattr(option, 'name'):
                                    option_type = getattr(option, 'type', 'value')
                                    options.append(f"{option.name}:{option_type}")
                                else:
                                    options.append(str(option))
                            commandJson = {
                                **base_data,
                                "name": command.name,
                                "description": command.description,
                                "usage": f"/{command.name} " + " ".join([f"[{opt}]" for opt in options]),
                                "type": "slash",
                                "examples": getattr(command, 'examples', []),
                            }
                        
                        commands.append(commandJson)
                    except Exception as e:
                        self.logger.error(f"Error processing command {command.name}: {str(e)}")
                self.commands = commands
            return self.commands

        @self.route("get_detailed_stats")
        async def get_detailed_stats(_):
            process = psutil.Process()
            
            # Get bot statistics from UserManager
            bot_user_manager = UserManager(self.bot.user)
            bot_stats_summary = bot_user_manager.get_bot_stats_summary()
            
            # System stats
            system_stats = {
                "cpu_usage": round(psutil.cpu_percent(), 2),
                "memory_usage": round(process.memory_percent(), 2),
                "memory_total": psutil.virtual_memory().total,
                "python_version": platform.python_version(),
                "os": f"{platform.system()} {platform.release()}",
                "process_uptime": round(process.create_time(), 2),
                "thread_count": process.num_threads(),
                "disk_usage": round(psutil.disk_usage('/').percent, 2)
            }

            # Bot stats with BotStatistics data
            bot_stats = {
                "guild_count": len(self.bot.guilds),
                "user_count": sum(g.member_count for g in self.bot.guilds),
                "channel_count": sum(len(g.channels) for g in self.bot.guilds),
                "voice_connections": len(self.bot.voice_clients),
                "latency": round(self.bot.latency * 1000),
                "uptime": (datetime.now() - self.bot.start_time).total_seconds(),
                "command_count": len(get_commands_func("")),
                "cogs_loaded": len(self.bot.cogs),
                "shard_count": self.bot.shard_count or 1,
                "current_shard": getattr(self.bot, "shard_id", 0),
                # Add BotStatistics data
                "messages_sent": bot_stats_summary.get("messages_sent", 0),
                "commands_processed": bot_stats_summary.get("commands_processed", 0),
                "errors_encountered": bot_stats_summary.get("errors", 0),
            }

            # User activity stats
            try:
                user_data = load_json_files("Data/Users/")
                activity_stats = analyze_data(user_data)
            except Exception as e:
                self.logger.error(f"Error loading user stats: {str(e)}")
                activity_stats = {}

            # Guild details
            guild_stats = []
            for guild in self.bot.guilds:
                guild_stats.append({
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
                })

            # Message activity (last 24h)
            # Note: You'll need to implement message tracking elsewhere
            message_stats = {
                "total_messages_24h": getattr(self.bot, "messages_24h", 0),
                "commands_used_24h": getattr(self.bot, "commands_used_24h", 0),
            }

            # Command usage stats
            command_stats = {}
            for cmd in self.bot.get_application_commands():
                command_stats[cmd.name] = getattr(cmd, "uses", 0)

            return {
                "system": system_stats,
                "bot": bot_stats,
                "activity": activity_stats,
                "guilds": guild_stats,
                "messages": message_stats,
                "commands": command_stats,
                "timestamp": datetime.now().timestamp()
            }

        @self.route("get_guild_stats")
        async def get_guild_stats(data):
            guild_id = data.get("guild_id")
            guild = self.bot.get_guild(guild_id)
            
            if not guild:
                return {"error": "Guild not found"}

            # Get detailed guild statistics
            return {
                "basic_info": {
                    "name": guild.name,
                    "id": guild.id,
                    "owner": str(guild.owner),
                    "created_at": guild.created_at.timestamp(),
                    "icon_url": str(guild.icon.url) if guild.icon else None,
                },
                "members": {
                    "total": guild.member_count,
                    "online": len([m for m in guild.members if m.status != "offline"]),
                    "bots": len([m for m in guild.members if m.bot]),
                    "humans": len([m for m in guild.members if not m.bot])
                },
                "channels": {
                    "total": len(guild.channels),
                    "text": len(guild.text_channels),
                    "voice": len(guild.voice_channels),
                    "categories": len(guild.categories),
                    "forums": len([c for c in guild.channels if isinstance(c, ForumChannel)]),
                    "stages": len(guild.stage_channels)
                },
                "other": {
                    "roles": len(guild.roles),
                    "emojis": len(guild.emojis),
                    "stickers": len(guild.stickers),
                    "boost_level": guild.premium_tier,
                    "boost_count": guild.premium_subscription_count,
                    "features": list(guild.features),
                    "verification_level": str(guild.verification_level),
                    "explicit_content_filter": str(guild.explicit_content_filter),
                    "mfa_level": guild.mfa_level
                }
            }

    async def _start_server(self):
        """Internal method to run the IPC server in its own event loop."""
        self.logger.info("Starting IPC server...")
        self.server.start()

    def start(self):
        """Start the IPC server in a separate thread."""
        self.setup_default_routes()
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_server())
        
        self.logger.info("Starting IPC server in a separate thread...")
        server_thread = Thread(target=run_server, daemon=True)
        server_thread.start()