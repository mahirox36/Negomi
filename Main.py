import traceback
from typing import Generator, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import nextcord
from nextcord.ext import commands
import ollama
from requests import get
from rich.traceback import install
from modules.Nexon import *
# from modules.updater import AutoUpdater

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = nextcord.Intents.all()
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            max_messages=1000,
            heartbeat_timeout=150.0,
            guild_ready_timeout=5.0,
            owner_id=overwriteOwner if overwriteOwner else None
        )
        
        self.start_time = datetime.now()
        
        self.owner: Optional[User] = owner # type: ignore
        self._cleanup_done = asyncio.Event()
        
        # Setup logging
        self.logger = logger
        
        # self.version = "0.7.0"  # Set your current version
        # self.updater = AutoUpdater("mahirox36", "Negomi", self.version)
        
        self.setup_hook()

    async def cleanup(self):
        """Cleanup bot resources"""
        if self._cleanup_done.is_set():
            return

        self.logger.info("Starting cleanup process...")
        
        for vc in self.voice_clients:
            try: await vc.disconnect(force=True)
            except: pass

        try: await self.close()
        except: pass

        self._cleanup_done.set()
        self.logger.info("Cleanup completed")

    def setup_hook(self) -> None:
        """Overridden setup hook to handle bundled and non-bundled extensions."""
        if is_executable():
            # Check for updates
            self.logger.info("Checking for updates...")
            if self.updater.check_for_updates():
                self.logger.info("Update available! Downloading...")
                if new_exe := self.updater.download_update():
                    self.logger.info("Applying update...")
                    self.updater.apply_update(new_exe)
            else:
                self.logger.info("Up to date!")

            # Load extensions normally
            data = [i for i in self._load_extensions(get=True)]
            
        else:
            data = [i for i in self._load_extensions    (get=True)]
    
    def _load_extensions(self, get: bool = False) -> Union[None, Generator[Path, Path, Path]]:
        """Load all extension modules with executable-aware path handling."""
        self.logger.info("Starting extension loading process")

        try:
            # Handle different base paths for exe vs normal running
            if is_executable():
                # When running as exe, we need to check sys._MEIPASS
                if hasattr(sys, '_MEIPASS'):
                    base_path = Path(sys._MEIPASS)
                else:
                    base_path = Path.cwd()
                extensions_path = base_path / "classes"
            else:
                extensions_path = Path("classes")

            self.logger.info(f"Using extensions path: {extensions_path.resolve()}")

            # Verify extensions directory exists
            if not extensions_path.exists():
                self.logger.error(f"Extensions directory not found at: {extensions_path.resolve()}")
                if get:
                    return []
                return None

            # Modify the import path to include our extensions directory
            if str(extensions_path.parent) not in sys.path:
                sys.path.insert(0, str(extensions_path.parent))
                self.logger.info(f"Added to sys.path: {extensions_path.parent}")

            loaded_extensions = []
            for ext_path in extensions_path.rglob("*.py"):
                # Skip files based on existing conditions
                if (ext_path.stem == "__init__" or
                    "pycache" in str(ext_path) or 
                    "Working on Progress" in str(ext_path) or
                    "." in ext_path.stem or
                    (not enableAI and ext_path.stem == "AI") or
                    (not Welcome_enabled and ext_path.stem == "Welcome") or
                    (get and ext_path.stem == "testShadow")):
                    self.logger.debug(f"Skipping {ext_path.stem}")
                    continue
                
                if enableAI: 
                    try:
                        ollama.list()
                    except: 
                        logger.error("Ollama isn't installed, skipping AI\nTo Install Ollama Go to this link: https://ollama.com/download")
                        continue
                
                try:
                    # Construct module name relative to the classes directory
                    rel_path = ext_path.relative_to(extensions_path.parent)
                    ext_name = str(rel_path.with_suffix('')).replace('\\', '.').replace('/', '.')

                    self.load_extension(ext_name)
                    self.logger.info(f"Successfully loaded extension: {ext_name}")

                    loaded_extensions.append(ext_path)
                    if get:
                        yield ext_path

                except Exception as e:
                    self.logger.error(f"Failed to load extension {ext_path.name}: {str(e)}")
                    self.logger.error(f"Traceback: {traceback.format_exc()}")

            self.logger.info(f"Extension loading complete. Loaded {len(loaded_extensions)} extensions")

        except Exception as e:
            self.logger.error(f"Critical error during extension loading: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            if get:
                return []
            return None

        if not get:
            return None

    async def on_ready(self) -> None:
        """Handler for when the bot is ready."""
        if not hasattr(self, '_ready_called'):
            global owner
            self.owner = await set_owner(self) # type: ignore
            owner = self.owner
            logger.info(f"Owner Have been set to {get_name(self.owner)}") # type: ignore
            self._ready_called = True
            
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


    async def _send_startup_message(self) -> None:
        """Send startup notification to bot owner"""
        try:
            if self.owner != None:
                channel = await self.owner.create_dm()
                await channel.send(
                    embed=nextcord.Embed(
                        title="Status Update",
                        description="Bot has successfully started",
                        color=colors.Info.value
                    )
                )
            else:
                logger.warning("There is no owner")
        except Exception as e:
            self.logger.warning(f"Failed to send startup message: {str(e)}")



async def main():
    bot = DiscordBot()
    try:
        await bot.start(token)
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
        await bot.cleanup()
        input()
    

if __name__ == "__main__":
    install()  # Install Rich traceback handler
    asyncio.run(main())