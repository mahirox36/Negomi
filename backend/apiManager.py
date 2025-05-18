from __future__ import annotations

from datetime import datetime
import asyncio
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from functools import lru_cache
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

from .features.cache import CacheManager
from .features.storage import StorageManager
from .tasks import start_tasks


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
    """Manages FastAPI server and route handlers"""

    def __init__(
        self,
        config: APIConfig,
        cache: CacheManager,
        storage: StorageManager,
        client: commands.Bot,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.cache = cache
        self.storage = storage
        self.client = client
        self.oauth_sessions: Dict[str, OAuth2Session] = {}
        self.start_time = utils.utcnow()
        self.rate_limit_store: Dict[str, List[float]] = {}
        self.background_tasks = BackgroundTasks()
        self._server = None
        self._shutdown_event = asyncio.Event()
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
            description="API for bot dashboard",
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

    @lru_cache(maxsize=1000)
    async def _cached_fetch_user(self, user_id: int, cache_ttl: Optional[int] = None):
        user = self.client.get_user(user_id)
        if not user:
            try:
                user = await self.client.fetch_user(user_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="User not found")
        return user

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

    async def start(self) -> None:
        """Start the FastAPI server with graceful shutdown"""
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

    async def shutdown(self) -> None:
        """Gracefully shutdown the server"""
        if self._server:
            self.logger.info("Shutting down API server...")
            self._server.should_exit = True
            await self._cleanup()
            self._server = None

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        # OAuth2Session does not require explicit closing
        self.oauth_sessions.clear()
        self.rate_limit_store.clear()

    async def verify_auth(self, request: Request) -> Optional[str]:
        """Verify authentication and return access token if valid"""
        access_token = request.cookies.get("accessToken")
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Get or create OAuth session
        if access_token not in self.oauth_sessions:
            oauth_token = OAuth2Token(
                {"access_token": access_token, "token_type": "Bearer"}
            )
            self.oauth_sessions[access_token] = OAuth2Session(
                self.oauth_client, oauth_token
            )

        try:
            session = self.oauth_sessions[access_token]
            user = await session.fetch_user()

            self.cache.cache_user(access_token, user)

        except Exception as e:
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

    async def fetch_user(self, user_id: int):
        user = self.client.get_user(user_id)
        if not user:
            try:
                user = await self.client.fetch_user(user_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="User not found")
        return user

    async def fetch_guild(self, guild_id: int):
        guild = self.client.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.client.fetch_guild(guild_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Guild not found")
        return guild

    async def fetch_channel(self, channel_id: int):
        channel = self.client.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.client.fetch_channel(channel_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Channel not found")
        return channel
