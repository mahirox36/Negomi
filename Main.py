from rich.traceback import install
install()

import traceback
from typing import Generator, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import nextcord
from nextcord.ext.commands import MissingPermissions, NotOwner, NoPrivateMessage, PrivateMessageOnly
import ollama
from modules.Nexon import *
import multiprocessing
from Dashboard.dashboard import run_dashboard

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = nextcord.Intents.all()
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            lazy_load_commands=False,
            owner_id=overwriteOwner if overwriteOwner else None,
            help_command=None
            
        )
        
        self.start_time = datetime.now()
        
        self.owner: Optional[User] = owner # type: ignore
        self._cleanup_done = asyncio.Event()
        
        # Setup logging
        self.logger = logger
        
        # Initialize IPC
        if dashboard_enabled:
            self.ipc_manager: Optional[IPCManager] = IPCManager(self)
        
        self.setup_hook()

    async def cleanup(self):
        """Cleanup bot resources including IPC"""
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
        """Setup hook with IPC initialization"""
        data = [i for i in self._load_extensions(get=True)]
        if dashboard_enabled:
            self.ipc_manager.start()
    
    def _load_extensions(self, get: bool = False) -> Union[None, Generator[Path, Path, Path]]:
        """Load all extension modules with executable-aware path handling."""
        self.logger.info("Starting extension loading process")

        try:
            extensions_path = Path("classes")

            self.logger.debug(f"Using extensions path: {extensions_path.resolve()}")

            # Verify extensions directory exists
            if not extensions_path.exists():
                self.logger.error(f"Extensions directory not found at: {extensions_path.resolve()}")
                if get:
                    return []
                return None

            # Modify the import path to include our extensions directory
            if str(extensions_path.parent) not in sys.path:
                sys.path.insert(0, str(extensions_path.parent))
                self.logger.debug(f"Added to sys.path: {extensions_path.parent}")

            loaded_extensions = []
            for ext_path in extensions_path.rglob("*.py"):
                # Skip files based on existing conditions
                if (ext_path.stem == "__init__" or
                    "pycache" in str(ext_path) or 
                    "Working on Progress" in str(ext_path) or
                    "Arc" in str(ext_path) or
                    "." in ext_path.stem or
                    (not enableAI and ext_path.stem == "AI") or
                    (not Welcome_enabled and ext_path.stem == "Welcome")):
                    self.logger.debug(f"Skipping {ext_path.stem}")
                    continue
                
                if enableAI and ext_path.stem == "AI": 
                    if isClientOnline() is offline:
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
            
            self.logger.info(f"{get_name(self.user)} is online!")
            
            if send_to_owner_enabled:
                await self._send_startup_message()


    async def _send_startup_message(self) -> None:
        """Send startup notification to bot owner"""
        try:
            if self.owner != None:
                channel = await self.owner.create_dm()
                message: Message = await channel.send(
                    embed=nextcord.Embed(
                        title="Status Update",
                        description="Bot has successfully started",
                        color=colors.Info.value
                    )
                )
                self.logger.info(f"Sent to {get_name(self.owner)} ({self.owner.id}) with the message ID {message.id}")
            else:
                logger.warning("There is no owner")
        except Exception as e:
            self.logger.warning(f"Failed to send startup message: {str(e)}")
    
    
    #ERROR HANDLERS
    async def on_application_command_error(self, ctx: Interaction, error: Exception):
        try:
            err = error.original
        except AttributeError:
            err = error
        if isinstance(err, SlashCommandOnCooldown):
            await ctx.response.send_message(
                embed=error_embed(f"You're on cooldown! Try again in {err.time_left:.2f} seconds.", "Too Fast"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationMissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.response.send_message(
                embed=error_embed(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNotOwner):
            await ctx.response.send_message(
                embed=error_embed(f"You are not the owner of the bot", "Not Owner"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNotOwnerGuild):
            await ctx.response.send_message(
                embed=error_embed(f"You are not the owner of the Server {err.guild}", "Not Owner of Server"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNoPrivateMessage):
            await ctx.response.send_message(
                embed=error_embed(f"You can't Use this command in DM", "DM not Allowed"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationPrivateMessageOnly):
            await ctx.response.send_message(
                embed=error_embed(f"You Only Can Do this Command in DM", "DM Only"),
                ephemeral=True)
            return
        elif isinstance(error, FeatureDisabled):
            if error.send_error: await ctx.response.send_message(
                embed=error_embed(error.message,"Feature Disabled",))
            return 
        elif isinstance(error, CommandDisabled):
            return
        if not ctx.response.is_done():
            await ctx.response.send_message(embed=error_embed(error,title="An unexpected error occurred"))
        logger.error(error)
    
        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)
        
        # with open("logs/error_traceback.py", "w") as f:
        #     f.write(error_details)
        buffer = io.BytesIO()
        buffer.write(error_details.encode('utf-8'))
        buffer.seek(0)
            
        channel = await self.owner.create_dm()

        await channel.send(content="New Error Master!", file=File(buffer,"error_traceback.py"))
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"You're on cooldown! Try again in {error.retry_after:.2f} seconds.")
            return
        elif isinstance(error, MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await ctx.reply(
                embed=error_embed(f"You don't have {missing}", "Missing Permissions"))
            return
        elif isinstance(error, NotOwner):
            await ctx.reply(
                embed=error_embed(f"You are not the owner of the bot", "Not Owner"))
            return
        elif isinstance(error, FeatureDisabled):
            if error.send_error: await ctx.reply(
                embed=error_embed(f"This Feature is disabled",
                                  "Feature Disabled"))
            return 
        # elif isinstance(error, NotOwnerGuild):
        #     await ctx.reply(
        #         embed=error_embed(f"You are not the owner of the Server {error.guild}", "Not Owner of Server"),
        #         ephemeral=True)
        #     return
        elif isinstance(error, NoPrivateMessage):
            await ctx.reply(
                embed=error_embed(f"You can't Use this command in DM", "DM not Allowed"),
                ephemeral=True)
            return
        elif isinstance(error, PrivateMessageOnly):
            await ctx.reply(
                embed=error_embed(f"You Only Can Do this Command in DM", "DM Only"),
                ephemeral=True)
            return
        elif isinstance(error,commands.errors.CommandNotFound):
            return
        elif isinstance(error, CommandDisabled):
            return
        await ctx.reply(embed=error_embed(error,title="An unexpected error occurred"))
        logger.error(error)
    
        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)
        
        buffer = io.BytesIO()
        buffer.write(error_details.encode('utf-8'))
        buffer.seek(0)
            
        channel = await self.owner.create_dm()

        await channel.send(content="New Error Master!", file=File(buffer,"error_traceback.py"))
    async def on_error(self, event_method: str, *args: Any, **kwargs: Any):
        self.logger.error(f"Traceback in {event_method}: {traceback.format_exc()}")



async def main():
    bot = DiscordBot()
    
    # Start dashboard in separate process
    if dashboard_enabled:
        dashboard_process = multiprocessing.Process(target=run_dashboard)
        dashboard_process.start()
    
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
        dashboard_process.terminate()
        await bot.cleanup()
        input()
    

if __name__ == "__main__":
    asyncio.run(main())