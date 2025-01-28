import asyncio
from datetime import datetime
from nextcord.ext import ipc
from typing import Callable, Dict
from threading import Thread
from .config import BotConfig
from .logger import logger

class IPCManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logger
        self.routes: Dict[str, Callable] = {}
        self.server = ipc.Server(
            bot=self.bot,
            secret_key=BotConfig.IPC.secret,
            port=BotConfig.IPC.port or 25401,
            do_multicast=False
        )
        
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

        @self.route("get_bot_stats")
        async def get_bot_stats(_):
            return {
                "guild_count": len(self.bot.guilds),
                "user_count": sum(g.member_count for g in self.bot.guilds),
                "ping": round(self.bot.latency * 1000),
                "uptime": (datetime.now() - self.bot.start_time).total_seconds()
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