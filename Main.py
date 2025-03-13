from rich.traceback import install

from nexon.badge import BadgeManager
install()

import traceback
from typing import Generator
from pathlib import Path
import asyncio
from datetime import datetime
import nexon
from nexon.ext.commands import MissingPermissions
from modules.Nexon import *

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = nexon.Intents.all()
        super().__init__(
            command_prefix="u.",
            intents=intents,
            lazy_load_commands=False,
            owner_id=overwriteOwner if overwriteOwner else None,
            help_command=None,
            logger_level=Level,
            enable_user_data=True
        )
        
        self.start_time = datetime.now()
        
        self._cleanup_done = asyncio.Event()
        
        # Setup logging
        self.logger = logger
        
        BadgeManager().set_badge_earned_callback(self.onBadgeEarned)
        
        self.setup_hook()
    
    async def onBadgeEarned(self, user: nexon.User, badge: nexon.Badge):
        embed = Embed.Info(
            title=f"🏆 New Badge Earned: {badge.name}!",
            description=badge.description
        )
        
        if badge.icon_url:
            embed.set_thumbnail(url=badge.icon_url)
            
        embed.add_field(
            name="Unlocked",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=False
        )
        
        # Try to DM the user
        try:
            await user.send(embed=embed)
        except: pass
    
    async def on_interaction(self, interaction: Interaction) -> None:
        if interaction.type == InteractionType.application_command and interaction.data is not None:
            command_id = interaction.data.get("id")
            if command_id is not None:
                command = self.get_application_command(int(command_id))
                if command is None:
                    return await super().on_interaction(interaction)
        else:
            return await super().on_interaction(interaction)
        if not interaction.guild:
            return await super().on_interaction(interaction)
        cog_name = command.parent_cog.__class__.__name__ 
        if cog_name and FeatureManager(interaction.guild.id, cog_name).is_disabled():
            await interaction.response.send_message(
                embed=Embed.Error("This Feature is disabled", "Feature Disabled"),ephemeral=True
            )
            return
            
        await super().on_interaction(interaction)
            
    
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
        extensions = self._load_extensions(get=True)
        data = [i for i in extensions] if extensions is not None else []
    
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
                skip_conditions = [
                    ext_path.stem == "__init__",
                    "pycache" in str(ext_path),
                    "Working on Progress" in str(ext_path),
                    "Arc" in str(ext_path),
                    "." in ext_path.stem,
                    not enableAI and ext_path.stem == "AI"
                ]

                # Skip if any condition is met
                if any(skip_conditions):
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
            self._ready_called = True
            
            await self.change_presence(
                activity=nexon.Activity(
                    type=nexon.ActivityType.watching,
                    name=Presence
                ),
                status=nexon.Status.idle if debug else nexon.Status.online
            )
            
            await self.sync_application_commands()
            
            self.logger.info(f"{self.user.display_name if self.user else 'Bot'} is online!")
            
            if send_to_owner_enabled:
                await self._send_startup_message()


    async def _send_startup_message(self) -> None:
        """Send startup notification to bot owner"""
        try:
            owner = self.get_user(self.owner_id) # type: ignore
            if owner is None:
                owner= await self.fetch_user(self.owner_id) # type: ignore
            channel = await owner.create_dm()
            author = [self.user.display_name if self.user else 'Bot', self.user.avatar.url if self.user and self.user.avatar else None]
            message: Message = await channel.send(
                embed=nexon.Embed.Info(
                    title="Status Update",
                    description="Bot has successfully started",
                    author=author,
                )
            )
            self.logger.info(f"Sent to {owner.display_name} ({owner.id}) with the message ID {message.id}")
        except Exception as e:
            self.logger.warning(f"Failed to send startup message: {str(e)}")
    
    
    #ERROR HANDLERS
    async def on_application_command_error(self, ctx: Interaction, error: Exception):
        if isinstance(error, ApplicationInvokeError):
            err = error.original
        else:
            err = error
        logger.info(str(type(err)))
        if isinstance(err, ApplicationOnCooldown):
            await ctx.response.send_message(
                embed=Embed.Error(f"You're on cooldown! Try again in {err.time_left:.2f} seconds.", "Too Fast"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationMissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.response.send_message(
                embed=Embed.Error(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationNotOwner):
            await ctx.response.send_message(
                embed=Embed.Error(f"You are not the owner of the bot", "Not Owner"),
                ephemeral=True)
            return
        # elif isinstance(err, ApplicationNotOwnerGuild):
        #     await ctx.response.send_message(
        #         embed=Embed.Error(f"You are not the owner of the Server {err.guild}", "Not Owner of Server"),
        #         ephemeral=True)
        #     return
        elif isinstance(err, ApplicationNoPrivateMessage):
            await ctx.response.send_message(
                embed=Embed.Error(f"You can't Use this command in DM", "DM not Allowed"),
                ephemeral=True)
            return
        elif isinstance(err, ApplicationPrivateMessageOnly):
            await ctx.response.send_message(
                embed=Embed.Error(f"You Only Can Do this Command in DM", "DM Only"),
                ephemeral=True)
            return
        elif isinstance(err, FeatureDisabled):
            if err.send_error: await ctx.response.send_message(
                embed=Embed.Error("This Feature is disabled","Feature Disabled",), ephemeral=True)
            return
        elif isinstance(err, MissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.response.send_message(
                embed=Embed.Error(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True
            )
            return
        
        elif isinstance(err, Forbidden):
            await ctx.response.send_message(
                embed=Embed.Error("I don't have permission to do this", "Missing Permissions"),
                ephemeral=True
            )
            return
        if not ctx.response.is_done():
            await ctx.response.send_message(embed=Embed.Error(str(err), title="An unexpected error occurred"))
        else:
            await ctx.followup.send(embed=Embed.Error(str(err), title="An unexpected error occurred"))
        logger.error(error)
    
        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)
        
        # with open("logs/error_traceback.py", "w") as f:
        #     f.write(error_details)
        buffer = io.BytesIO()
        buffer.write(error_details.encode('utf-8'))
        buffer.seek(0)
            
        owner = self.get_user(self.owner_id)  # type: ignore
        if owner is None:
            owner = await self.fetch_user(self.owner_id)  # type: ignore
        channel = await owner.create_dm()

        await channel.send(content="New Error Master!", file=File(buffer,"error_traceback.py"))
    async def on_error(self, event_method: str, *args: Any, **kwargs: Any):
        self.logger.error(f"Traceback in {event_method}: {traceback.format_exc()}")



async def main():
    bot = DiscordBot()
    
    try:
        await bot.start(token)
    except nexon.LoginFailure:
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
    asyncio.run(main())