from typing import Optional, List, Union
import logging
import sys
from pathlib import Path
import asyncio
from datetime import datetime
import platform
import signal

import nextcord
from nextcord.ext import commands, ipc, tasks
from nextcord import AppInfo, TeamMember, Interaction
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from modules.Side import *

class DiscordBot(commands.Bot):
    def __init__(self):
        # Initialize with optimized intents
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = False  # Disable if not needed
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            chunk_guilds_at_startup=False,  # Disable member chunking unless needed
            max_messages=1000,
            heartbeat_timeout=150.0,  # Increased heartbeat timeout
            guild_ready_timeout=5.0,
        )
        
        self.start_time = datetime.now()
        self.app_info: Optional[AppInfo] = None
        
        # Connection monitoring
        self.last_heartbeat = datetime.now()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.latency_threshold = 5.0
        self.connection_lock = asyncio.Lock()
        self._cleanup_done = asyncio.Event()
        
        # Setup logging
        self.console = Console()
        self.logger = logger
        
        # IPC Server setup
        if IpcEnabled:
            self.ipc = ipc.Server(
                bot=self,
                secret_key=IpcPassword,
                host=IpcHost,
                port=IpcPort
            )
        
        # Setup signal handlers and background tasks
        self._setup_signal_handlers()
        self.setup_hook()
        
        
    def _setup_signal_handlers(self):
        """Setup handlers for system signals"""
        if platform.system() != 'Windows':
            signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.cleanup()))
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.cleanup()))

    @tasks.loop(seconds=30.0)
    async def monitor_connection(self):
        """Monitor bot connection health"""
        try:
            if self.is_ws_ratelimited():
                self.logger.warning("WebSocket is being rate limited!")
                
            current_latency = self.latency
            if current_latency > self.latency_threshold:
                self.logger.warning(f"High latency detected: {current_latency:.2f}s")
                
            time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
            if time_since_heartbeat > self.latency_threshold:
                self.logger.warning(f"Connection issues detected. Time since last heartbeat: {time_since_heartbeat:.2f}s")
                await self._handle_connection_issue()
                
        except Exception as e:
            self.logger.error(f"Error in connection monitoring: {str(e)}")

    async def _handle_connection_issue(self):
        """Handle connection issues"""
        async with self.connection_lock:
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                self.logger.error("Max reconnection attempts reached. Starting cleanup...")
                await self.cleanup()
                return

            self.reconnect_attempts += 1
            self.logger.info(f"Attempting to reconnect... Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            
            try:
                await self.close()
                await asyncio.sleep(5)
                await self.start(token)
            except Exception as e:
                self.logger.error(f"Reconnection failed: {str(e)}")

    def start_background_tasks(self):
        """Start background monitoring tasks"""
        self.monitor_connection.start()

    async def cleanup(self):
        """Cleanup bot resources"""
        if self._cleanup_done.is_set():
            return

        self.logger.info("Starting cleanup process...")
        
        self.monitor_connection.cancel()
        
        for vc in self.voice_clients:
            try:
                await vc.disconnect(force=True)
            except:
                pass

        try:
            await self.close()
        except:
            pass

        self._cleanup_done.set()
        self.logger.info("Cleanup completed")

    @staticmethod
    def _setup_logging() -> logging.Logger:
        """Setup Rich logging with proper formatting"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(logging.INFO,rich_tracebacks=True)]
        )
        logger = logging.getLogger("discord_bot")
        return logger

    def setup_hook(self) -> None:
        """Setup hook that runs before the bot starts"""
        self._load_extensions()
        self.start_background_tasks()
        
    def _load_extensions(self) -> None:
        """Load all extension modules"""
        extensions_path = Path("./classes")
        for ext_path in extensions_path.rglob("*.py"):
            if ext_path.stem == "__init__":
                continue
                
            if "pycache" in str(ext_path) or "Working on Progress" in str(ext_path):
                continue
                
            if "." in ext_path.stem:
                self.logger.error(f"Invalid extension name: {ext_path.stem} (contains dots)")
                continue
                
            if DisableAiClass and ext_path.stem == "AI":
                continue
                
            if not Welcome_enabled and ext_path.stem == "Welcome":
                continue

            try:
                ext_name = f"{str(ext_path.parent).replace("\\",".")}.{ext_path.stem}"
                self.load_extension(ext_name)
                self.logger.info(f"Loaded extension: {ext_name}")
            except Exception as e:
                self.logger.error(f"Failed to load extension {ext_name}: {str(e)}")

    async def on_ready(self) -> None:
        """Handler for when the bot is ready."""
        if not hasattr(self, '_ready_called'):
            self._ready_called = True
            self.app_info = await self.application_info()
            
            await self.change_presence(
                activity=nextcord.Activity(
                    type=nextcord.ActivityType.watching,
                    name=Presence
                )
            )
            
            await self.sync_all_application_commands()
            
            self.logger.info(f"{self.user.display_name} is online!")
            
            if send_to_owner_enabled:
                await self._send_startup_message()
    
    async def on_socket_raw_receive(self, msg):
        """Handle raw socket messages"""
        self.last_heartbeat = datetime.now()

    async def on_socket_response(self, msg):
        """Handle socket responses"""
        try:
            if msg and msg.get('op') == 11:  # Heartbeat ACK
                self.last_heartbeat = datetime.now()
                self.reconnect_attempts = 0
        except:
            pass

    async def _send_startup_message(self) -> None:
        """Send startup notification to bot owner"""
        try:
            if self.app_info.owner.name.startswith("team"):
                user = self.get_user(self.app_info.team.owner.id)
            else:
                user = self.app_info.owner
                
            if user:
                channel = await user.create_dm()
                await channel.send(
                    "Bot is Online ✅",
                    embed=nextcord.Embed(
                        title="Status Update",
                        description="Bot has successfully started",
                        color=nextcord.Color.green()
                    )
                )
        except Exception as e:
            self.logger.error(f"Failed to send startup message: {str(e)}")

    async def on_ipc_ready(self) -> None:
        """Handler for when IPC server is ready"""
        self.logger.info("IPC server is ready")

    async def on_ipc_error(self, endpoint: str, error: Exception) -> None:
        """Handler for IPC errors"""
        self.logger.error(f"IPC endpoint {endpoint} raised: {str(error)}")

def main():
    bot = DiscordBot()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if platform.system() == 'Windows':
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        
        loop.slow_callback_duration = 0.25
        
        loop.run_until_complete(bot.start(token))
    except nextcord.LoginFailure:
        bot.logger.error("""
        Failed to login. Please check:
        1. Your token in the config file
        2. Token validity at https://discord.com/developers/applications
        3. Reset token if necessary
        """)
    except Exception as e:
        bot.logger.exception("An error occurred while running the bot")
    finally:
        loop.run_until_complete(bot.cleanup())
        loop.close()

if __name__ == "__main__":
    install()  # Install Rich traceback handler
    main()