from typing import Generator, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import nextcord
from nextcord.ext import commands
from rich.traceback import install
from modules.Nexon import *

#TODO: Make the app if it was builded download the classes and check their version and updated if needed

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
        
        self.owner: Optional[User] = owner
        self._cleanup_done = asyncio.Event()
        
        # Setup logging
        self.logger = logger
        
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
        if is_bundled():
            self._setup_bundled()
        else:
            data = [i for i in self._load_extensions(get=True)]
            github = "https://raw.githubusercontent.com/mahirox36/Negomi/refs/heads/main/"
            OptionalClasses = ["AI", "debug", "Help", "Welcome"]
            discarded = ["ipc"]
            JsonData = {
                "Optional": [],
                "Classes": []
            }
            for file in data:
                if file.stem in discarded:
                    continue
                fileLink = github + str(file)
                if file.stem in OptionalClasses:
                    JsonData["Optional"].append({"name": file.stem, "link": fileLink})
                else:
                    JsonData["Classes"].append(fileLink)
            with open("classes/classes.json", "w") as f:
                json.dump(JsonData, f, indent= 4)
        
    
    
    def _setup_bundled(self):
        FeaturesPath = Path("classes/Features/")
        OtherPath = Path("classes/Other/")
        #TODO: make it download the file from the github file "Classes"

    
    
    def _load_extensions(self, get: bool = False) -> Union[None, Generator[Path, Path, Path]]:
        """Load all extension modules."""
        extensions_path = Path("./classes")
        for ext_path in extensions_path.rglob("*.py"):
            if (ext_path.stem == "__init__" or
                "pycache" in str(ext_path) or "Working on Progress" in str(ext_path) or
                "." in ext_path.stem or
                (DisableAiClass and ext_path.stem == "AI") or
                (not Welcome_enabled and ext_path.stem == "Welcome") or
                (get and ext_path.stem == "testShadow")):
                continue
            
            try:
                ext_name = f"{str(ext_path.parent).replace('\\', '.')}.{ext_path.stem}"
                self.load_extension(ext_name)
                self.logger.info(f"Loaded extension: {ext_name}")
                yield ext_path
            except Exception as e:
                self.logger.warning(f"Failed to load extension {ext_name}: {str(e)}")

    async def on_ready(self) -> None:
        """Handler for when the bot is ready."""
        if not hasattr(self, '_ready_called'):
            global owner
            self.owner = await set_owner(self)
            logger.info(f"Owner Have been set to {get_name(self.owner)}")
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

    async def on_ipc_ready(self) -> None:
        """Handler for when IPC server is ready"""
        self.logger.info("IPC server is ready")

    async def on_ipc_error(self, endpoint: str, error: Exception) -> None:
        """Handler for IPC errors"""
        self.logger.error(f"IPC endpoint {endpoint} raised: {str(error)}")



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