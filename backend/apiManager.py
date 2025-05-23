from __future__ import annotations

from datetime import datetime
import asyncio
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from modules.Nexon import debug, config as configDiscord, utils
from nexon.OAuth2 import OAuth2Client, OAuth2Session, OAuth2Token
from nexon import IntegrationType
from nexon.ext import commands
from nexon import (
    MessageApplicationCommand,
    UserApplicationCommand,
    SlashApplicationCommand,
    SlashApplicationSubcommand,
)
from nexon.data.models import UserBadge
from nexon.abc import GuildChannel
from .features.storage import StorageManager
from .tasks import start_tasks
from modules.Nexon import TextChannel, VoiceChannel

# Import the new cache system
from .features.cache import (
    cache_manager, 
    cache_integration, 
    cached, 
    Priority,
    get_cached_guilds,
    get_cached_user,
    warm_cache
)


class APIConfig:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 25400,
        allowed_origins: Optional[list[str]] = None,
        rate_limit_requests: int = 300,
        rate_limit_window: int = 180,
        cache_ttl: int = 900,
    ) -> None:
        self.host = host
        self.port = port
        self.allowed_origins = allowed_origins or [
            "https://negomi.mahirou.online",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.cache_ttl = cache_ttl


class APIServer:
    """Manages FastAPI server and route handlers with advanced caching"""

    def __init__(
        self,
        config: APIConfig,
        storage: StorageManager,
        client: commands.Bot,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.storage = storage
        self.client = client
        self.oauth_sessions: Dict[str, OAuth2Session] = {}
        self.start_time = utils.utcnow()
        self.rate_limit_store: Dict[str, List[float]] = {}
        self.background_tasks = BackgroundTasks()
        self._server = None
        self._shutdown_event = asyncio.Event()
        
        # NEW: Initialize the advanced cache system
        self.cache = cache_integration
        
        DEFAULT_OAUTH_SCOPES = [
            "identify",
            "guilds",
            "email",
        ]
        if debug:
            self.oauth_client = OAuth2Client(
                client_id=configDiscord.oauth.client_id,
                client_secret=configDiscord.oauth.client_secret,
                redirect_uri=configDiscord.oauth.debug_redirect_url,
                scopes=DEFAULT_OAUTH_SCOPES,
            )
        else:
            self.oauth_client = OAuth2Client(
                client_id=configDiscord.oauth.client_id,
                client_secret=configDiscord.oauth.client_secret,
                redirect_uri=configDiscord.oauth.redirect_url,
                scopes=DEFAULT_OAUTH_SCOPES,
            )

        # Initialize FastAPI
        self.app = FastAPI(
            title="Bot Dashboard API",
            description="API for bot dashboard with advanced caching",
            version="2.0.0",
            docs_url="/api/docs" if debug else None,
            redoc_url="/api/redoc" if debug else None,
        )

        self._setup_middleware()
        self._setup_routes()

        # Store backend reference
        self.app.state.backend = self

    async def _rate_limit_check(self, ip: str) -> bool:
        now = utils.utcnow().timestamp()
        if ip not in self.rate_limit_store:
            self.rate_limit_store[ip] = []

        # Remove old timestamps
        self.rate_limit_store[ip] = [
            ts
            for ts in self.rate_limit_store[ip]
            if now - ts <= self.config.rate_limit_window
        ]

        if len(self.rate_limit_store[ip]) >= self.config.rate_limit_requests:
            return False

        self.rate_limit_store[ip].append(now)
        return True

    # NEW: Enhanced cached user fetching with advanced cache
    @cached(ttl=3600, priority=Priority.HIGH, tags={"discord", "users"})
    async def fetch_user_cached(self, user_id: int):
        """Cached user fetching with advanced cache system"""
        user = self.client.get_user(user_id)
        if not user:
            try:
                user = await self.client.fetch_user(user_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="User not found")
        return user

    # NEW: Enhanced cached guild fetching
    @cached(ttl=1800, priority=Priority.HIGH, tags={"discord", "guilds"})
    async def fetch_guild_cached(self, guild_id: int):
        """Cached guild fetching with advanced cache system"""
        guild = self.client.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.client.fetch_guild(guild_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Guild not found")
        return guild

    # NEW: Enhanced cached channel fetching
    @cached(ttl=1200, priority=Priority.MEDIUM, tags={"discord", "channels"})
    async def fetch_channel_cached(self, channel_id: int):
        """Cached channel fetching with advanced cache system"""
        channel = self.client.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.client.fetch_channel(channel_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Channel not found")
        return channel

    # NEW: Enhanced cached commands fetching
    @cached(ttl=7200, priority=Priority.MEDIUM, tags={"bot", "commands"})
    async def get_commands_of_bot_cached(self) -> List[Dict[str, Any]]:
        """Get all bot commands with metadata - cached version"""
        return await self.get_commands_of_bot()

    def _setup_middleware(self) -> None:
        """Setup CORS and other middleware"""

        @self.app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            client_ip = request.client.host if request.client else "unknown"
            if not await self._rate_limit_check(client_ip):
                return JSONResponse(
                    status_code=429, content={"detail": "Too many requests"}
                )
            return await call_next(request)

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

    def _setup_routes(self) -> None:
        """Setup API routes"""
        # Import route modules here to avoid circular imports
        from .api.v1 import router as router_v1

        self.app.include_router(router_v1)
        
        # NEW: Add cache management routes
        self._setup_cache_routes()

    def _setup_cache_routes(self) -> None:
        """Setup cache management routes"""
        
        @self.app.get("/api/cache/stats")
        async def get_cache_stats():
            """Get comprehensive cache statistics"""
            try:
                stats = await cache_manager.get_stats()
                return JSONResponse(stats)
            except Exception as e:
                self.logger.error(f"Error getting cache stats: {e}")
                raise HTTPException(status_code=500, detail="Failed to get cache stats")
        
        @self.app.post("/api/cache/invalidate/{tag}")
        async def invalidate_cache_by_tag(tag: str):
            """Invalidate cache entries by tag"""
            try:
                invalidated = await cache_manager.invalidate_by_tags({tag})
                return JSONResponse({
                    "success": True, 
                    "invalidated_count": invalidated,
                    "tag": tag
                })
            except Exception as e:
                self.logger.error(f"Error invalidating cache tag {tag}: {e}")
                raise HTTPException(status_code=500, detail="Failed to invalidate cache")
        
        @self.app.post("/api/cache/warm")
        async def warm_cache_endpoint():
            """Warm cache with common queries"""
            try:
                # Define common patterns to pre-cache
                patterns = [
                    (self.get_commands_of_bot_cached, [], {}),
                    # Add more patterns as needed
                ]
                await warm_cache(patterns)
                return JSONResponse({"success": True, "message": "Cache warmed successfully"})
            except Exception as e:
                self.logger.error(f"Error warming cache: {e}")
                raise HTTPException(status_code=500, detail="Failed to warm cache")

    async def start(self) -> None:
        """Start the FastAPI server with graceful shutdown and cache initialization"""
        # NEW: Start the cache system
        await cache_manager.start_background_tasks()
        self.logger.info("Advanced cache system initialized")
        
        # Warm the cache with common data
        try:
            await self._warm_initial_cache()
        except Exception as e:
            self.logger.warning(f"Cache warming failed: {e}")
        
        await start_tasks(self)
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_config=None,
            loop="asyncio",
            reload=debug,
        )
        self._server = uvicorn.Server(config)
        try:
            self.logger.info(
                f"Starting API server on {self.config.host}:{self.config.port}"
            )
            await self._server.serve()
        except Exception as e:
            self.logger.error(f"Failed to start API server: {str(e)}")
            await self._cleanup()
            raise

    async def _warm_initial_cache(self):
        """Warm cache with initial data"""
        try:
            # Pre-cache bot commands
            await self.get_commands_of_bot_cached()
            
            # Pre-cache common guild data if available
            # You can add more warming patterns here
            
            self.logger.info("Initial cache warming completed")
        except Exception as e:
            self.logger.warning(f"Initial cache warming failed: {e}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the server and cache system"""
        if self._server:
            self.logger.info("Shutting down API server...")
            self._server.should_exit = True
            
            # NEW: Stop cache background tasks
            await cache_manager.stop_background_tasks()
            self.logger.info("Cache system stopped")
            
            await self._cleanup()
            self._server = None

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        # OAuth2Session does not require explicit closing
        self.oauth_sessions.clear()
        self.rate_limit_store.clear()

    async def verify_auth(self, request: Request) -> Optional[str]:
        """Verify authentication and return access token if valid - Enhanced with caching"""
        access_token = request.cookies.get("accessToken")
        if not access_token:
            self.logger.warning("Access token not found in cookies")
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Check the advanced cache first
        cached_user = await self.cache.get_cached_user(access_token)
        if cached_user:
            # Validate cached user data
            if "id" in cached_user and "username" in cached_user:
                self.logger.debug("User found in cache")
                return access_token
            else:
                self.logger.warning("Cached user data is invalid")

        # Get or create OAuth session
        if access_token not in self.oauth_sessions:
            self.logger.info("Creating new OAuth session for access token")
            oauth_token = OAuth2Token(
                {"access_token": access_token, "token_type": "Bearer"}
            )
            self.oauth_sessions[access_token] = OAuth2Session(
                self.oauth_client, oauth_token
            )

        try:
            session = self.oauth_sessions[access_token]
            user = await session.fetch_user()

            # Convert user object to dictionary and cache it
            self.cache.cache_user(access_token, user) # type: ignore

        except Exception as e:
            self.logger.error(f"Error during session fetch: {e}")
            # Clear invalid session and raise an error
            if access_token in self.oauth_sessions:
                del self.oauth_sessions[access_token]
            raise HTTPException(status_code=401, detail="Invalid token")

        return access_token

    async def get_commands_of_bot(self) -> List[Dict[str, Any]]:
        """Get all bot commands with metadata"""
        commands = []
        for command in self.client.get_all_application_commands():
            try:
                if hasattr(command, "children") and command.children: # type: ignore
                    self._process_subcommands(command, commands)  # type: ignore
                    continue
                guild_installed = (
                    IntegrationType.guild_install in command.integration_types
                    if command.integration_types
                    else True
                )
                user_installed = (
                    IntegrationType.user_install in command.integration_types
                    if command.integration_types
                    else False
                )
                if command.parent_cog and len(command.parent_cog.application_commands) == 1:
                    category = "Other"
                elif command.parent_cog:
                    category = command.parent_cog.__class__.__name__
                else:
                    category = "No Category"
                command_data = {
                    "name": command.qualified_name,
                    "description": command.description or "",
                    "category": category,
                    "admin_only": (
                        getattr(command, "default_member_permissions", None) is not None
                        and command.default_member_permissions is not None
                    ),
                    "guild_only": getattr(command, "guild_only", False),
                    "permissions": [],
                    "cooldown": getattr(command, "cooldown", None),
                    "examples": getattr(command, "examples", []),
                    "guild_installed": guild_installed,
                    "user_installed": user_installed,
                    "usage": f"/{command.qualified_name}",
                    "type": self._get_type(command),
                }
                commands.append(command_data)

            except Exception as e:
                self.logger.error(
                    f"Error processing command {command.qualified_name}: {str(e)}"
                )

        return commands

    def _get_command_options(self, command: Any) -> List[str]:
        """Get command options in a readable format"""
        options = []
        for option in getattr(command, "options", []):
            if isinstance(option, str):
                options.append(option)
            elif hasattr(option, "name"):
                option_type = getattr(option, "type", "value")
                options.append(f"{option.name}:{option_type}")
            else:
                options.append(str(option))
        return options

    def _process_subcommands(
        self,
        Main_command: Union[SlashApplicationCommand, SlashApplicationSubcommand],
        commands_list: List[Dict[str, Any]],
        parent_command: Optional[SlashApplicationCommand] = None,
    ) -> None:
        """Process subcommands recursively"""

        for _, child in Main_command.children.items():
            if child.children:
                if isinstance(Main_command, SlashApplicationCommand):
                    # If the child is a subcommand group, process its children
                    self._process_subcommands(
                        child, commands_list, Main_command
                    )
                else:
                    # If the child is a subcommand, process its children
                    self._process_subcommands(
                        child, commands_list
                    )
            else:
                parent_cmd: SlashApplicationCommand = parent_command if parent_command else Main_command # type: ignore
                if not parent_cmd.integration_types:
                    guild_installed = True
                    user_installed = False
                else:
                    guild_installed = (
                        IntegrationType.guild_install in parent_cmd.integration_types
                        if parent_cmd.integration_types
                        else True
                    )
                    user_installed = (
                        IntegrationType.user_install in parent_cmd.integration_types
                        if parent_cmd.integration_types
                        else False
                    )
                command_data = {
                    "name": child.qualified_name,
                    "description": child.description or "",
                    "category": (
                        parent_cmd.parent_cog.__class__.__name__
                        if parent_cmd.parent_cog
                        else "No Category"
                    ),
                    "admin_only": (
                        getattr(parent_cmd, "default_member_permissions", None) is not None
                        and parent_cmd.default_member_permissions is not None
                    ),
                    "guild_only": getattr(child, "guild_only", False),
                    "permissions": [],
                    "cooldown": getattr(child, "cooldown", None),
                    "examples": getattr(child, "examples", []),
                    "guild_installed": guild_installed,
                    "user_installed": user_installed,
                    "usage": f"/{child.qualified_name}",
                    "type": self._get_type(child),
                }
                commands_list.append(command_data)

    def _get_type(self, command: Any) -> str:
        """Get command type"""
        if isinstance(command, UserApplicationCommand):
            return "user"
        elif isinstance(command, MessageApplicationCommand):
            return "message"
        elif isinstance(command, (SlashApplicationCommand, SlashApplicationSubcommand)):
            return "slash"
        else:
            self.logger.warning(f"Unknown command type: {type(command)}")
            return "unknown"

    def _get_usage(self, command: Any, command_name: str) -> str:
        type = self._get_type(command)
        options = self._get_command_options(command)
        if type == "slash":
            return f"/{command_name} " + " ".join(f"[{opt}]" for opt in options)
        elif type == "user":
            return f"Right-click user → Apps → {command_name}"
        elif type == "message":
            return f"Right-click message → Apps → {command_name}"
        else:
            return "unknown"

    # NEW: Use cached versions for better performance
    async def fetch_user(self, user_id: int):
        """Fetch user with caching"""
        return await self.fetch_user_cached(user_id)

    async def fetch_guild(self, guild_id: int):
        """Fetch guild with caching"""
        return await self.fetch_guild_cached(guild_id)

    async def fetch_channel(self, channel_id: int):
        """Fetch channel with caching"""
        return await self.fetch_channel_cached(channel_id)

    async def fetch_message(self, message_id: int, channel_id: int):
        """Fetch message with channel caching"""
        try:
            channel = await self.fetch_channel_cached(channel_id)
            if not isinstance(channel, (TextChannel, VoiceChannel)):
                raise HTTPException(
                    status_code=400, detail="Cannot fetch message from a private channel"
                )
            else:
                # Messages are typically not cached due to high volume and frequent changes
                message = await channel.fetch_message(message_id)
        except Exception as e:
            return False
        return message

    # NEW: Cache management methods
    async def invalidate_user_cache(self, user_id: int):
        """Invalidate cache for a specific user"""
        await cache_manager.invalidate_by_tags({"discord", "users"})
    
    async def invalidate_guild_cache(self, guild_id: int):
        """Invalidate cache for a specific guild"""
        await cache_manager.invalidate_by_tags({"discord", "guilds"})
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return await cache_manager.get_stats()