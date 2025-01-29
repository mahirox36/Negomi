import asyncio
from datetime import datetime
from nextcord.ext import ipc
from nextcord.ext.commands import Bot
from nextcord import UserApplicationCommand, SlashApplicationCommand
from typing import Callable, Dict, List, Optional
from threading import Thread
from .config import BotConfig
from .logger import logger

class IPCManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logger
        self.routes: Dict[str, Callable] = {}
        self.server = ipc.Server(
            bot=self.bot,
            secret_key=BotConfig.IPC.secret,
            port=BotConfig.IPC.port or 25401,
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
            self.logger.info(self.bot.user.display_avatar.url)
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