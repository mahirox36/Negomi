from nexon import IntegrationType, SlashApplicationCommand, UserApplicationCommand, MessageApplicationCommand
from modules.Nexon import debug, config, split_frontend
from modules.Nexon import logger
from nexon.ext import commands
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from aiohttp import ClientSession, ClientTimeout
from typing import Any, Dict, List, Optional
from mypy_boto3_s3 import S3Client
from cachetools import TTLCache
from datetime import datetime
from api import v1
import uvicorn
import asyncio
import boto3
import time
import uuid


class DashboardCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.app = FastAPI(
            title="Bot Dashboard API",
            description="API for bot dashboard",
            version="2.0.0"
        )
        self.app.state.backend = self
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
        
        # Initialize S3 client with validation
        try:
            logger.info(config.cloudflare.endpoint)
            if not config.cloudflare.endpoint or not config.cloudflare.endpoint.startswith(('http://', 'https://')):
                self.logger.error("Invalid Cloudflare endpoint URL. Must start with http:// or https://")
                self.s3_client = None
            else:
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=config.cloudflare.endpoint.rstrip('/'),  # Remove trailing slashes
                    aws_access_key_id=config.cloudflare.access_key_id,
                    aws_secret_access_key=config.cloudflare.secret_access_key,
                    region_name="auto"  # Add default region
                )
        except Exception as e:
            self.logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
        
        self.register_routes()

    def register_routes(self):
        self.app.include_router(v1.admin.router, prefix="/api/v1/admin")
        self.app.include_router(v1.auth.router, prefix="/api/v1/auth")
        self.app.include_router(v1.bot.router, prefix="/api/v1/bot")
        self.app.include_router(v1.guilds.router, prefix="/api/v1/guilds")
        self.app.include_router(v1.layout.router, prefix="/api/v1/layout")
        
    
    
    def upload_image(self, file, filename: str):
        """Uploads an image file to Cloudflare R2 and returns the public URL."""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 client not initialized")
        try:
            unique_filename = f"{uuid.uuid4()}-{filename}"
            self.s3_client.upload_fileobj(
                file.file, 
                config.cloudflare.bucket_name, 
                unique_filename, 
                ExtraArgs={"ACL": "public-read"}
            )
            return (
                f"{config.cloudflare.public_bucket_url.rstrip('/')}/{unique_filename}",
                f"{config.cloudflare.endpoint.rstrip('/')}/{config.cloudflare.bucket_name}/{unique_filename}"
            )
        except Exception as e:
            self.logger.error(f"Failed to upload image: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload image")
    
    def delete_image(self, filename: str):
        """Deletes an image file from Cloudflare R2."""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 client not initialized")
        try:
            self.s3_client.delete_object(
                Bucket=config.cloudflare.bucket_name,
                Key=filename
            )
            return {"detail": "Image deleted successfully"}
        except Exception as e:
            self.logger.error(f"Failed to delete image: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete image")
    
    def get_commands_func(self):
        if not self.commands:
            commands = []
            for command in self.client.get_application_commands():
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
        guild = self.client.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.client.fetch_guild(guild_id)
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