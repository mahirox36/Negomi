from __future__ import annotations

import asyncio
import logging
from typing import Optional
from contextlib import AsyncExitStack
from nexon.ext import commands
from .apiManager import APIServer, APIConfig
from .features.storage import StorageManager, StorageConfig
from modules.Nexon import config, debug, utils

class DashboardCog(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger("bot")
        self._exit_stack = AsyncExitStack()
        self._initialized = False
        # Initialize managers with enhanced error handling
        try:
            
            storage_config = StorageConfig(
                endpoint=config.cloudflare.endpoint,
                access_key=config.cloudflare.access_key_id,
                secret_key=config.cloudflare.secret_access_key,
                bucket_name=config.cloudflare.bucket_name,
                public_url=config.cloudflare.public_bucket_url
            )
            self.storage = StorageManager(storage_config)
            
            api_config = APIConfig(
                rate_limit_requests=200,
                rate_limit_window=60,
                cache_ttl=300
            )
            self.api = APIServer(
                config=api_config,
                storage=self.storage,
                client=self.client
            )
            
            self._initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard components: {str(e)}")
            raise

    async def cog_load(self) -> None:
        """Initialize components and start frontend if needed"""
        try:
            if not self._initialized:
                raise RuntimeError("Dashboard components not properly initialized")
                
            # Register cleanup handlers
            await self._exit_stack.enter_async_context(self.storage)
                
        except Exception as e:
            self.logger.error(f"Failed to load dashboard components: {str(e)}")
            await self.cleanup()
            raise

    async def cog_unload(self) -> None:
        """Cleanup all resources"""
        self.logger.info("Unloading dashboard cog...")
        await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup resources in correct order"""
        try:
            if hasattr(self, 'api'):
                await self.api.shutdown()
            await self._exit_stack.aclose()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Start dashboard API server when bot is ready"""     
        if not self._initialized:
            self.logger.error("Cannot start dashboard - not properly initialized")
            return
            
        try:
            task = asyncio.create_task(self.api.start())
            task.add_done_callback(self._handle_api_task_done)
            
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {str(e)}")
            await self.cleanup()
            raise

    def _handle_api_task_done(self, task: asyncio.Task) -> None:
        """Handle API server task completion"""
        try:
            task.result()
        except asyncio.CancelledError:
            self.logger.info("API server shutdown gracefully")
        except Exception as e:
            self.logger.error(f"API server error: {str(e)}")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(DashboardCog(bot))