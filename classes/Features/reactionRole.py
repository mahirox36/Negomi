from modules.Nexon import *
from nexon.data.models import Messages
from nexon.errors import NotFound
import time
import asyncio
from typing import Union, Optional, Tuple
import logging

from nexon.raw_models import RawReactionActionEvent

logger = logging.getLogger(__name__)


class ReactionRole(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.user_cooldowns = {}

    async def _validate_user_reaction(
        self,
        user: Member,
        reaction_role: dict,
        guild: Guild,
        channel: TextChannel,
        message: Message,
    ) -> Tuple[bool, str]:
        # Check cooldown
        if reaction_role.get("cooldown"):
            user_key = f"{user.id}_{message.id}"
            last_use = self.user_cooldowns.get(user_key, 0)
            if time.time() - last_use < reaction_role["cooldown"]:
                return False, "You must wait before selecting another role"
            self.user_cooldowns[user_key] = time.time()

        # Check required roles
        if reaction_role.get("require_roles"):
            has_required = any(
                role.id in reaction_role["require_roles"] for role in user.roles
            )
            if not has_required:
                return False, "You don't have the required roles"

        # Check forbidden roles
        if reaction_role.get("forbidden_roles"):
            has_forbidden = any(
                role.id in reaction_role["forbidden_roles"] for role in user.roles
            )
            if has_forbidden:
                return False, "You have a role that prevents you from selecting this"

        # Check max reactions per user
        if reaction_role.get("max_reactions_per_user"):
            try:
                user_roles = list(
                    set(
                        [
                            user.get_role(int(reaction["role_id"]))
                            for reaction in reaction_role["reactions"]
                            if user.get_role(int(reaction["role_id"]))
                        ]
                    )
                )
                logger.info(f"User {user.id} has roles: {user_roles}")
                logger.info(
                    f"User {user.id} has {len(user_roles)} roles from this reaction group"
                )
                if len(user_roles) >= reaction_role["max_reactions_per_user"]:
                    return (
                        False,
                        f"You can only have {reaction_role['max_reactions_per_user']} roles from this reaction group",
                    )
            except Exception as e:
                logger.error(f"Error checking max roles: {e}")

        return True, ""

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        reaction = payload.emoji

        guild = (
            self.client.get_guild(payload.guild_id)
            if payload.guild_id is not None
            else None
        )
        if not guild:
            return
        user = guild.get_member(payload.user_id)
        if not user:
            try:
                user = await guild.fetch_member(payload.user_id)
            except NotFound:
                return
        if user.bot:
            return

        channel = guild.get_channel(payload.channel_id)
        if not isinstance(channel, TextChannel):
            return

        Logger = Logs.Logger(guild=guild, user=user, cog=self)
        await Logger.debug(
            "ReactionRole: User reacted",
            context={
                "user": user.id,
                "message_id": payload.message_id,
                "emoji": str(payload.emoji),
                "channel_id": channel.id,
            },
        )
        reaction_id = (
            payload.emoji.name if payload.emoji.is_unicode_emoji() else payload.emoji.id
        )
        feature = await Feature.get_guild_feature_or_none(
            feature_name="reaction_roles",
            guild_id=guild.id,
        )
        if not feature or not feature.enabled:
            return

        reaction_roles = feature.get_setting("reaction_roles", [])
        message = await Messages.get(message_id=payload.message_id)
        if not message:
            return

        reaction_role = next(
            (rr for rr in reaction_roles if str(rr["message_id"]) == str(message.id)),
            None,
        )
        if not reaction_role:
            return

        reaction_config = next(
            (
                r
                for r in reaction_role["reactions"]
                if str(r.get("emoji")) == str(reaction_id)
                or r.get("url") == str(payload.emoji.url)
            ),
            None,
        )
        if not reaction_config:
            return

        message = await channel.fetch_message(payload.message_id)
        can_react, error_message = await self._validate_user_reaction(
            user, reaction_role, guild, channel, message
        )

        try:
            role = guild.get_role(reaction_config["role_id"])
            if not role:
                role = await guild.fetch_role(reaction_config["role_id"])
        except NotFound:
            await Logger.warning(
                "Role not found", context={"role_id": reaction_config["role_id"]}
            )
            return

        if not can_react and role not in user.roles:
            try:
                await user.send(
                    embed=Embed.Warning(
                        title="Reaction Role", description=error_message
                    )
                    .set_author(
                        name=guild.name, icon_url=guild.icon.url if guild.icon else None
                    )
                    .set_footer(text=f"Guild ID: {guild.id}")
                )
            except Exception as e:
                await Logger.error(
                    "Failed to send DM to user", context={"error": str(e)}
                )
            if reaction_role.get("remove_reactions", True):

                actual_reaction = next(
                    (r for r in message.reactions if str(r.emoji) == str(reaction)),
                    None,
                )
                if actual_reaction:
                    try:
                        await actual_reaction.remove(user)
                    except:
                        await Logger.error(
                            "Failed to remove reaction",
                            context={"reaction": str(reaction)},
                        )
            return

        if role in user.roles:
            if reaction_role.get("allow_unselect", True):
                await user.remove_roles(role, reason="ReactionRole: Unselected role")
                try:
                    await user.send(
                        embed=Embed.Info(
                            title="Reaction Role",
                            description=f"You have unselected the role: {role.name} in {channel.mention}",
                        )
                        .set_author(
                            name=guild.name,
                            icon_url=guild.icon.url if guild.icon else None,
                        )
                        .set_footer(text=f"Guild ID: {guild.id}")
                    )
                except Exception as e:
                    await Logger.error(
                        "Failed to send DM to user", context={"error": str(e)}
                    )
                if reaction_role.get("remove_reactions", True):
                    message = await channel.fetch_message(payload.message_id)
                    actual_reaction = next(
                        (r for r in message.reactions if str(r.emoji) == str(reaction)),
                        None,
                    )
                    if actual_reaction:
                        try:
                            await actual_reaction.remove(user)
                        except:
                            await Logger.error(
                                "Failed to remove reaction",
                                context={"reaction": str(reaction)},
                            )
            else:
                try:
                    await user.send(
                        embed=Embed.Warning(
                            title="Reaction Role",
                            description="You cannot unselect this role",
                        )
                        .set_author(
                            name=guild.name,
                            icon_url=guild.icon.url if guild.icon else None,
                        )
                        .set_footer(text=f"Guild ID: {guild.id}")
                    )
                except Exception as e:
                    await Logger.error(
                        "Failed to send DM to user", context={"error": str(e)}
                    )
                if reaction_role.get("remove_reactions", True):
                    message = await channel.fetch_message(payload.message_id)
                    actual_reaction = next(
                        (r for r in message.reactions if str(r.emoji) == str(reaction)),
                        None,
                    )
                    if actual_reaction:
                        try:
                            await actual_reaction.remove(user)
                        except:
                            await Logger.error(
                                "Failed to remove reaction",
                                context={"reaction": str(reaction)},
                            )
        else:
            await user.add_roles(role, reason="ReactionRole: Added role")
            try:
                await user.send(
                    embed=Embed.Info(
                        title="Reaction Role",
                        description=f"You have selected the role: {role.name} in {channel.mention}",
                    )
                    .set_author(
                        name=guild.name, icon_url=guild.icon.url if guild.icon else None
                    )
                    .set_footer(text=f"Guild ID: {guild.id}")
                )
            except Exception as e:
                await Logger.error(
                    "Failed to send DM to user", context={"error": str(e)}
                )
            if reaction_role.get("remove_reactions", True):
                message = await channel.fetch_message(payload.message_id)
                actual_reaction = next(
                    (r for r in message.reactions if str(r.emoji) == str(reaction)),
                    None,
                )
                if actual_reaction:
                    try:
                        await actual_reaction.remove(user)
                    except:
                        await Logger.error(
                            "Failed to remove reaction",
                            context={"reaction": str(reaction)},
                        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        reaction = payload.emoji

        guild = (
            self.client.get_guild(payload.guild_id)
            if payload.guild_id is not None
            else None
        )
        if not guild:
            if payload.guild_id is not None:
                guild = await self.client.fetch_guild(payload.guild_id)
            else:
                return
        user = guild.get_member(payload.user_id)
        if not user:
            try:
                user = await guild.fetch_member(payload.user_id)
            except NotFound:
                return
        if user.bot:
            return

        Logger = Logs.Logger(guild=guild, user=user, cog=self)
        reaction_id = (
            reaction.name if payload.emoji.is_unicode_emoji() else reaction.id
        )

        channel = guild.get_channel(payload.channel_id)
        if not channel:
            try:
                channel = await guild.fetch_channel(payload.channel_id)
            except NotFound:
                return
        # Check if the channel is a TextChannel
        if not isinstance(channel, TextChannel):
            return

        feature = await Feature.get_guild_feature_or_none(
            feature_name="reaction_roles",
            guild_id=guild.id,
        )
        if not feature or not feature.enabled:
            return

        reaction_roles = feature.get_setting("reaction_roles", [])
        # Fetch the message from the database using the channel ID and payload message ID
        message = await Messages.get(message_id=payload.message_id)
        if not message:
            return

        # Filter reaction roles that match the message ID
        reaction_role = next(
            (rr for rr in reaction_roles if str(rr["message_id"]) == str(message.id)),
            None,
        )
        if not reaction_role:
            return

        reaction_config = next(
            (
                r
                for r in reaction_role["reactions"]
                if str(r.get("emoji")) == str(reaction_id)
                or r.get("url") == str(payload.emoji.url)
            ),
            None,
        )
        if not reaction_config:
            return

        try:
            role = guild.get_role(reaction_config["role_id"])
            if not role:
                role = await guild.fetch_role(reaction_config["role_id"])
        except NotFound:
            await Logger.warning(
                "Role not found", context={"role_id": reaction_config["role_id"]}
            )
            return

        if role in user.roles and reaction_role.get("allow_unselect", True):
            await user.remove_roles(role, reason="ReactionRole: Unselected role")
            try:
                await user.send(
                    embed=Embed.Info(
                        title="Reaction Role",
                        description=f"You have unselected the role: {role.name} in {channel.mention}",
                    )
                    .set_author(
                        name=guild.name, icon_url=guild.icon.url if guild.icon else None
                    )
                    .set_footer(text=f"Guild ID: {guild.id}")
                )
            except Exception as e:
                await Logger.error(
                    "Failed to send DM to user", context={"error": str(e)}
                )
        else:
            try:
                await user.send(
                    embed=Embed.Warning(
                        title="Reaction Role",
                        description="You cannot unselect this role",
                    )
                    .set_author(
                        name=guild.name, icon_url=guild.icon.url if guild.icon else None
                    )
                    .set_footer(text=f"Guild ID: {guild.id}")
                )
            except Exception as e:
                await Logger.error(
                    "Failed to send DM to user", context={"error": str(e)}
                )


def setup(client):
    client.add_cog(ReactionRole(client))
