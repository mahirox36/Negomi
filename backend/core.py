from __future__ import annotations

import asyncio
import logging
from nexon.ext import commands
from .apiManager import APIServer, APIConfig
from .features.cache import CacheManager
from .features.storage import StorageManager, StorageConfig
from .features.process import ProcessManager
from modules.Nexon import config, debug, split_frontend

class DashboardCog(commands.Cog):
    """Main dashboard cog that coordinates all dashboard components"""
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger("bot")
        
        # Initialize managers
        self.cache = CacheManager()
        self.process = ProcessManager(debug=debug)
        
        # Storage manager setup
        storage_config = StorageConfig(
            endpoint=config.cloudflare.endpoint,
            access_key=config.cloudflare.access_key_id,
            secret_key=config.cloudflare.secret_access_key,
            bucket_name=config.cloudflare.bucket_name,
            public_url=config.cloudflare.public_bucket_url
        )
        self.storage = StorageManager(storage_config)
        
        # API server setup
        api_config = APIConfig()
        self.api = APIServer(
            config=api_config,
            cache=self.cache,
            storage=self.storage,
            client=self.client
        )

    async def cog_load(self) -> None:
        """Called when the cog is loaded"""
        if not split_frontend:
            await self.process.start_frontend()

    async def cog_unload(self) -> None:
        """Called when the cog is unloaded"""
        await self.process.cleanup()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Start dashboard when bot is ready"""
        try:
            asyncio.create_task(self.api.start())
            
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {str(e)}")
            await self.process.cleanup()
            raise

def setup(bot: commands.Bot) -> None:
    """Add the dashboard cog to the bot"""
    bot.add_cog(DashboardCog(bot))