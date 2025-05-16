from enum import Enum
import traceback
import io
import logging
from typing import Optional, Dict, Any

# Import components
from .components.image_generator import WelcomeImageGenerator
from .components.cache_manager import WelcomeCacheManager
from .components.config_manager import WelcomeConfigManager
from .components.types import WelcomeStyle, ImageElementType

from modules.Nexon import *

logger = logging.getLogger("welcome")


class Welcome(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        # Initialize components
        self.cache_manager = WelcomeCacheManager()
        self.config_manager = WelcomeConfigManager()
        self.image_generator = WelcomeImageGenerator(self.cache_manager)

    def __del__(self):
        """Cleanup resources."""
        self.cache_manager.cleanup()

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """Handle new member joins with database integration."""
        if member.bot:
            return

        try:
            # Get config from the database
            config = await self.config_manager.get_welcome_config(member.guild.id)
            if not config or not config.get("enabled", True):
                return

            # Get channel with validation
            channel_id = config.get("channel_id")
            if not isinstance(channel_id, int):
                return
            channel = member.guild.get_channel(channel_id)
            if not channel:
                logger.warning(
                    f"Welcome channel {config.get('channel_id')} not found in {member.guild.id}"
                )
                return

            # Send welcome message
            if isinstance(channel, TextChannel):
                async with channel.typing():
                    await self.send_welcome_message(member, channel, config)

        except Exception as e:
            logger.error(f"Welcome error in {member.guild.id} for {member.id}: {e}")


    async def send_welcome_message(
        self,
        member: Member,
        channel: TextChannel,
        config: dict,
        ctx: Optional[Interaction] = None,
    ):
        """Send welcome message with enhanced features and animations"""
        try:
            message = await self.format_welcome_message(member, config["message"])
            style = config.get("style") or WelcomeStyle.TEXT.value

            match style:
                case WelcomeStyle.IMAGE.value:
                    if member.avatar:
                        cache_key = f"{member.guild.id}_{member.id}_{member.avatar.key}_{self.cache_manager.get_cache_version()}"
                        welcome_image = self.cache_manager.get_cached_image(cache_key)

                        if not welcome_image:
                            transformed_config = await self.config_manager.prepare_config_for_image_generation(
                                config
                            )
                            welcome_image = (
                                await self.image_generator.create_welcome_image(
                                    member.display_name,
                                    str(member.avatar.url),
                                    transformed_config["image_settings"],
                                )
                            )
                            self.cache_manager.cache_image(cache_key, welcome_image)
                            welcome_image.seek(0)

                        if welcome_image.getbuffer().nbytes == 0:
                            raise ValueError("Generated image is empty")

                        file = File(welcome_image, filename=f"welcome_{member.id}.png")
                        (
                            await channel.send(content=message, file=file)
                            if ctx is None
                            else await ctx.send(
                                content=message,
                                file=file,
                                embed=Embed.Info(
                                    "☝️ Above is how the welcome message will appear"
                                ),
                                ephemeral=True,
                            )
                        )
                    else:
                        await channel.send(message)

                case WelcomeStyle.EMBED.value:
                    embed = Embed(
                        title=config.get(
                            "embed_title", f"Welcome to {member.guild.name}!"
                        ),
                        description=message,
                        color=config["embed_color"] or int(colors.Info.value),
                    )
                    if member.avatar:
                        embed.set_thumbnail(url=member.avatar.url)
                    if config["image_settings"].get("background_url"):
                        embed.set_image(url=config["image_settings"]["background_url"])
                    (
                        await channel.send(embed=embed)
                        if ctx is None
                        else await ctx.send(
                            embeds=[
                                embed,
                                Embed.Info(
                                    "☝️ Above is how the welcome message will appear"
                                ),
                            ],
                            ephemeral=True,
                        )
                    )

                case _:
                    (
                        await channel.send(message)
                        if ctx is None
                        else await ctx.send(
                            content=message,
                            embed=Embed.Info(
                                "☝️ Above is how the welcome message will appear"
                            ),
                            ephemeral=True,
                        )
                    )

            # Clean up the cache if needed
            self.cache_manager.cleanup_if_needed()

        except Exception as e:
            logger.error(
                f"Welcome message error in {member.guild.id}: {e}", exc_info=True
            )
            if ctx:
                await ctx.send(
                    embed=Embed.Error(
                        "Failed to preview welcome message. Check permissions and settings."
                    ),
                    ephemeral=True,
                )

    async def format_welcome_message(self, member: Member, message: str) -> str:
        """Safely format welcome message with fallbacks."""
        try:
            return str(message).format(
                server=member.guild.name,
                count=member.guild.member_count,
                mention=member.mention,
                name=member.display_name,
            )
        except Exception:
            return f"Welcome {member.mention} to {member.guild.name}!"


def setup(client):
    client.add_cog(Welcome(client))
