import time
from rich.traceback import install

from nexon import BadgeManager
from nexon.data.models import BotUser, GuildData
from nexon.enums import Rarity

install()

import traceback
from typing import Generator
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
import nexon
from nexon.ext.commands import MissingPermissions
from modules.Nexon import *
import os
import json
from nexon.ext.tasks import loop

logger = logging.getLogger("Negomi")


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
            enable_user_data=True,
        )

        self.start_time = utils.utcnow()
        self._cleanup_done = asyncio.Event()

        # Setup logging
        self.logger = logger

        BadgeManager().set_badge_earned_callback(self.onBadgeEarned)

        self.daily_task.start()
        
        self.setup_hook()

    async def onBadgeEarned(self, user: nexon.User, badge: nexon.Badge):
        """Handle badge earning notifications with rich embeds and fallback mechanisms."""
        now = utils.utcnow()

        # Create a visually appealing embed with badge details
        title = (
            f"🏆 Badge Unlocked: {badge.name}"
            if not badge.hidden
            else f"🏆 Hidden Badge Unlocked: {badge.name}"
        )
        embed = nexon.Embed(
            title=title,
            description=badge.description,
            color=await self._get_rarity_color(badge.rarity, badge.guild_id),
            timestamp=now,
        )

        # Add badge visual elements
        if badge.icon_url:
            embed.set_thumbnail(url=badge.icon_url)

        # Add badge metadata
        embed.add_field(
            name="Unlocked", value=f"<t:{int(now.timestamp())}:R>", inline=True
        )

        if badge.rarity:
            embed.add_field(
                name="Rarity",
                value=f"{badge.emoji or '✨'} {badge.rarity.name.title()}",
                inline=True,
            )

        if not badge.hidden and badge.id:
            embed.add_field(name="Badge ID", value=f"`{badge.id}`", inline=True)
        if badge.guild_id:
            guild = self.get_guild(badge.guild_id)
            if guild:
                embed.add_field(
                    name="Server", value=f"{guild.name} ({guild.id})", inline=True
                )

        # Add footer with collection hint
        embed.set_footer(text="Check your profile to see your badge collection!")

        # Try to DM the user with graceful fallback
        try:
            await user.send(embed=embed)
            self.logger.info(
                f"Badge notification sent to {user.display_name} ({user.id}) for badge: {badge.name}"
            )
        except Exception as e:
            self.logger.debug(
                f"Could not send badge notification to {user.id}: {str(e)}"
            )

            # If guild-specific, try to notify in guild if DM fails
            if badge.guild_id and user.mutual_guilds:
                for guild in user.mutual_guilds:
                    if guild.id == badge.guild_id:
                        try:
                            # Try to find a suitable channel for notification
                            for channel in guild.text_channels:
                                if channel.permissions_for(guild.me).send_messages:
                                    await channel.send(
                                        content=f"{user.mention}, you earned a new badge!",
                                        embed=embed,
                                    )
                                    break
                        except:
                            pass
                        break

    async def _get_rarity_color(self, rarity: Rarity, guild_id: int) -> int:
        """Return color based on badge rarity."""
        if not rarity:
            return 0x7289DA  # Discord Blurple default
        settings = await Feature.get_guild_feature(guild_id, "basic_settings")
        print(settings.settings)
        colors = {
            "common": settings.get_setting("commonColor", 0xFF1493),
            "uncommon": settings.get_setting("uncommonColor", 0x00FFB9),
            "rare": settings.get_setting("rareColor", 0xFF4500),
            "epic": settings.get_setting("epicColor", 0x32CD32),
            "legendary": settings.get_setting("legendaryColor", 0x9400D3),
            "mythic": settings.get_setting("mythicColor", 0x00FFFF),
            "unique": settings.get_setting("uniqueColor", 0x8B0000),
        }
        print(colors)

        # Convert any hex string colors to integers
        for key, value in colors.items():
            if isinstance(value, str) and value.startswith("#"):
                try:
                    colors[key] = int(value.lstrip("#"), 16)
                except ValueError:
                    # Keep default if conversion fails
                    pass

        return colors.get(rarity.name.lower(), 0xFF1493)

    async def on_interaction(self, interaction: Interaction) -> None:
        if (
            interaction.type == InteractionType.application_command
            and interaction.data is not None
        ):
            command_id = interaction.data.get("id")
            if command_id is not None:
                command = self.get_application_command(int(command_id))
                if command is None:
                    return await super().on_interaction(interaction)
        else:
            return await super().on_interaction(interaction)
        if not interaction.guild:
            return await super().on_interaction(interaction)
        # cog_name = command.parent_cog.__class__.__name__
        # if cog_name and FeatureManager(interaction.guild.id, cog_name).is_disabled():
        #     await interaction.response.send_message(
        #         embed=Embed.Error("This Feature is disabled", "Feature Disabled"),ephemeral=True
        #     )
        #     return

        await super().on_interaction(interaction)

    async def cleanup(self):
        """Cleanup bot resources including IPC"""
        
        await self.change_presence(
            activity=nexon.Activity(
                type=nexon.ActivityType.watching, name="Under Maintenance"
            ),
            status=nexon.Status.dnd,
        )
        
        if self._cleanup_done.is_set():
            return

        self.logger.info("Starting cleanup process...")

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

    def setup_hook(self) -> None:
        """Setup hook with IPC initialization"""
        extensions = self._load_extensions(get=True)
        data = [i for i in extensions] if extensions is not None else []

    def _load_extensions(
        self, get: bool = False
    ) -> Union[None, Generator[Path, Path, Path]]:
        """Load all extension modules with executable-aware path handling."""
        self.logger.info("Starting extension loading process")

        try:
            extensions_path = Path("classes")

            self.logger.debug(f"Using extensions path: {extensions_path.resolve()}")

            # Verify extensions directory exists
            if not extensions_path.exists():
                self.logger.error(
                    f"Extensions directory not found at: {extensions_path.resolve()}"
                )
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
                    not enableAI and ext_path.stem == "AI",
                    "components" in str(ext_path),
                    "Views" in str(ext_path),
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
                    ext_name = (
                        str(rel_path.with_suffix(""))
                        .replace("\\", ".")
                        .replace("/", ".")
                    )

                    self.load_extension(ext_name)
                    self.logger.info(f"Successfully loaded extension: {ext_name}")

                    loaded_extensions.append(ext_path)
                    if get:
                        yield ext_path

                except Exception as e:
                    self.logger.error(
                        f"Failed to load extension {ext_path.name}: {str(e)}"
                    )
                    self.logger.error(f"Traceback: {traceback.format_exc()}")

            self.load_extension("backend.core")
            self.logger.info(
                f"Extension loading complete. Loaded {len(loaded_extensions)} extensions"
            )

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
        if not hasattr(self, "_ready_called"):
            self._ready_called = True
            database_url = f"postgres://{config.database.username}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.db_name}"
            with open(".env", "w") as env_file:
                env_file.write(f"DATABASE_URL={database_url}\n")
            await nexon.init_db()
            await self.change_presence(
                activity=nexon.Activity(
                    type=nexon.ActivityType.watching, name=Presence
                ),
                status=nexon.Status.idle if debug else nexon.Status.online,
            )

            await self.sync_application_commands()

            self.logger.info(
                f"{self.user.display_name if self.user else 'Bot'} is online!"
            )

            if send_to_owner_enabled:
                await self._send_startup_message()
    
    async def on_guild_remove(self, guild: nexon.Guild) -> None:
        """Handler for when the bot leaves a guild."""
        self.logger.debug(f"Left guild: {guild.name} ({guild.id})")
        isDeleteDataInstantly = (await Feature.get_guild_feature(
            guild.id, "basic_settings"
        )).get_setting("isDeleteDataInstantly", False)
        if isDeleteDataInstantly:
            await Feature.delete_guild_features(guild.id)
            guild_data= await GuildData.get_or_none(id= guild.id)
            if guild_data:
                await guild_data.delete()
        else:
            await Feature.soft_delete_guild_features(guild.id)
            guild_data = await GuildData.get_or_none(id=guild.id)
            if guild_data:
                await guild_data.request_deletion()

    async def on_guild_join(self, guild: nexon.Guild) -> None:
        """Handler for when the bot joins a new guild."""
        self.logger.debug(f"Joined new guild: {guild.name} ({guild.id})")
        if not guild.public_updates_channel:
            return
        self.logger.debug(f"Following {guild.name} ({guild.id})")
        try:
            bot_announce_channel = self.get_channel(1338953197280034867)
            if not bot_announce_channel:
                bot_announce_channel = await self.fetch_channel(1338953197280034867)
            if not isinstance(bot_announce_channel, nexon.TextChannel):
                return

            await bot_announce_channel.follow(destination=guild.public_updates_channel)

        except Exception as e:
            self.logger.warning(f"Failed to follow channel: {str(e)}")
        
        # Cancel any existing deletion requests for the guild
        guild_data = await GuildData.get_or_none(id=guild.id)
        if guild_data and guild_data.is_pending_deletion():
            await guild_data.cancel_deletion()
        await Feature.cancel_soft_delete_guild_features(guild.id)

    async def _send_startup_message(self) -> None:
        """Send startup notification to bot owner"""
        try:
            owner = self.get_user(self.owner_id)  # type: ignore
            if owner is None:
                owner = await self.fetch_user(self.owner_id)  # type: ignore
            channel = await owner.create_dm()
            author = [
                self.user.display_name if self.user else "Bot",
                self.user.avatar.url if self.user and self.user.avatar else None,
            ]
            message: Message = await channel.send(
                embed=nexon.Embed.Info(
                    title="Status Update",
                    description="Bot has successfully started",
                    author=author,
                )
            )
            self.logger.info(
                f"Sent to {owner.display_name} ({owner.id}) with the message ID {message.id}"
            )
        except Exception as e:
            self.logger.warning(f"Failed to send startup message: {str(e)}")

    # ERROR HANDLERS
    async def on_application_command_error(self, ctx: Interaction, error: Exception):
        if isinstance(error, ApplicationInvokeError):
            err = error.original
        else:
            err = error
        if isinstance(err, ApplicationOnCooldown):
            await ctx.response.send_message(
                embed=Embed.Error(
                    f"You're on cooldown! Try again in {err.time_left:.2f} seconds.",
                    "Too Fast",
                ),
                ephemeral=True,
            )
            return
        elif isinstance(err, ApplicationMissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.response.send_message(
                embed=Embed.Error(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True,
            )
            return
        elif isinstance(err, ApplicationNotOwner):
            await ctx.response.send_message(
                embed=Embed.Error(f"You are not the owner of the bot", "Not Owner"),
                ephemeral=True,
            )
            return
        # elif isinstance(err, ApplicationNotOwnerGuild):
        #     await ctx.response.send_message(
        #         embed=Embed.Error(f"You are not the owner of the Server {err.guild}", "Not Owner of Server"),
        #         ephemeral=True)
        #     return
        elif isinstance(err, ApplicationNoPrivateMessage):
            await ctx.response.send_message(
                embed=Embed.Error(
                    f"You can't use this command in DM", "DM not Allowed"
                ),
                ephemeral=True,
            )
            return
        elif isinstance(err, ApplicationPrivateMessageOnly):
            await ctx.response.send_message(
                embed=Embed.Error(f"You only can do this command in DM", "DM Only"),
                ephemeral=True,
            )
            return
        elif isinstance(err, MissingPermissions):
            missing = ", ".join(err.missing_permissions)
            await ctx.response.send_message(
                embed=Embed.Error(f"You don't have {missing}", "Missing Permissions"),
                ephemeral=True,
            )
            return

        elif isinstance(err, Forbidden):
            await ctx.response.send_message(
                embed=Embed.Error(
                    "I don't have permission to do this", "Missing Permissions"
                ),
                ephemeral=True,
            )
            return
        if not ctx.response.is_done():
            await ctx.response.send_message(
                embed=Embed.Error(str(err), title="An unexpected error occurred")
            )
        else:
            await ctx.followup.send(
                embed=Embed.Error(str(err), title="An unexpected error occurred")
            )
        logger.error(error)

        # Send detailed traceback to the bot owner
        tb_str = traceback.format_exception(type(error), error, error.__traceback__)
        error_details = "".join(tb_str)

        # with open("logs/error_traceback.py", "w") as f:
        #     f.write(error_details)
        buffer = io.BytesIO()
        buffer.write(error_details.encode("utf-8"))
        buffer.seek(0)

        owner = self.get_user(self.owner_id)  # type: ignore
        if owner is None:
            owner = await self.fetch_user(self.owner_id)  # type: ignore
        channel = await owner.create_dm()

        await channel.send(
            content="New Error Master!", file=File(buffer, "error_traceback.py")
        )
        await BotUser.log_error(error_details)

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any):
        self.logger.error(f"Traceback in {event_method}: {traceback.format_exc()}")
    
    @loop(hours=23)
    async def daily_task(self):
        """Daily task to check for expired badges and send notifications."""
        self.logger.info("Running daily task")
        try:
            threshold = utils.utcnow() - timedelta(days=3)
            await Feature.filter(deletion_requested_at__lte=threshold).delete()
            await GuildData.filter(
                deletion_requested_at__lte=threshold
            ).delete()
        except Exception as e:
            self.logger.error(f"Error in daily task: {str(e)}")
    
    @daily_task.before_loop
    async def before_daily_task(self):
        await self.wait_until_ready()


async def main():
    bot = DiscordBot()

    try:
        await bot.start(token)
    except nexon.LoginFailure:
        bot.logger.error(
            """
        Failed to login. Please check:
        1. Your token in the config file
        2. Token validity at https://discord.com/developers/applications
        3. Reset token if necessary
        """
        )
    except KeyboardInterrupt:
        bot.logger.info("Bot stopped by user")
    except Exception as e:
        bot.logger.exception("An error occurred while running the bot")
    finally:
        await bot.cleanup()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(traceback.format_exc())
            time.sleep(5)
