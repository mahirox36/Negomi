from modules.Nexon import *
from nexon.data.models import Messages
from nexon.errors import NotFound
import time
import asyncio
from typing import Union, Optional, Tuple, Set
import logging

from nexon.raw_models import RawReactionActionEvent

logger = logging.getLogger(__name__)


class ReactionRole(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.user_cooldowns = {}
        self.processing_reactions: Set[str] = set()  # Track processing reactions to prevent race conditions
        self.bot_removed_reactions: Set[str] = set()  # More specific tracking

    def _get_reaction_key(self, user_id: int, message_id: int, emoji_str: str) -> str:
        """Generate unique key for reaction tracking"""
        return f"{user_id}_{message_id}_{emoji_str}"

    async def _get_user_reaction_roles(self, user: Member, reaction_role: dict) -> list:
        """Get all roles the user has from this reaction group"""
        user_roles = []
        for reaction in reaction_role.get("reactions", []):
            try:
                role_id = int(reaction["role_id"])
                role = user.get_role(role_id)
                if role:
                    user_roles.append(role)
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid role_id in reaction config: {e}")
        return user_roles

    async def _validate_user_reaction(
        self,
        user: Member,
        reaction_role: dict,
        guild: Guild,
        channel: TextChannel,
        message: Message,
        is_adding: bool = True
    ) -> Tuple[bool, str]:
        """Validate if user can add/remove a reaction role"""
        
        # Check cooldown only for adding reactions
        if is_adding and reaction_role.get("cooldown"):
            user_key = f"{user.id}_{message.id}"
            last_use = self.user_cooldowns.get(user_key, 0)
            cooldown_remaining = reaction_role["cooldown"] - (time.time() - last_use)
            if cooldown_remaining > 0:
                return False, f"You must wait {int(cooldown_remaining)} seconds before selecting another role"

        # Check required roles
        if reaction_role.get("require_roles"):
            user_role_ids = {role.id for role in user.roles}
            required_roles = set(reaction_role["require_roles"])
            if not required_roles.intersection(user_role_ids):
                return False, "You don't have the required roles"

        # Check forbidden roles
        if reaction_role.get("forbidden_roles"):
            user_role_ids = {role.id for role in user.roles}
            forbidden_roles = set(reaction_role["forbidden_roles"])
            if forbidden_roles.intersection(user_role_ids):
                return False, "You have a role that prevents you from selecting this"

        # Check max reactions per user (only when adding)
        if is_adding and reaction_role.get("max_reactions_per_user"):
            try:
                user_roles = await self._get_user_reaction_roles(user, reaction_role)
                current_count = len(user_roles)
                max_allowed = reaction_role["max_reactions_per_user"]
                
                logger.debug(f"User {user.id} has {current_count}/{max_allowed} roles from reaction group")
                
                if current_count >= max_allowed:
                    return False, f"You can only have {max_allowed} role(s) from this reaction group"
                    
            except Exception as e:
                logger.error(f"Error checking max roles for user {user.id}: {e}")
                return False, "Error validating role limits"

        return True, ""

    async def _safe_remove_reaction(self, message: Message, emoji, user: Member, logger_instance) -> bool:
        """Safely remove a reaction with proper error handling"""
        try:
            # Find the actual reaction object
            actual_reaction = None
            for reaction in message.reactions:
                if str(reaction.emoji) == str(emoji):
                    actual_reaction = reaction
                    break
            
            if actual_reaction:
                reaction_key = self._get_reaction_key(user.id, message.id, str(emoji))
                self.bot_removed_reactions.add(reaction_key)
                await actual_reaction.remove(user)
                return True
        except Exception as e:
            await logger_instance.error(
                "Failed to remove reaction",
                context={"reaction": str(emoji), "error": str(e)}
            )
        return False

    async def _send_user_notification(self, user: Member, embed: Embed, logger_instance):
        """Send DM notification to user with error handling"""
        try:
            await user.send(embed=embed)
        except Exception as e:
            await logger_instance.warning(
                "Failed to send DM notification", 
                context={"user_id": user.id, "error": str(e)}
            )

    async def _process_reaction_add(self, payload: RawReactionActionEvent):
        """Process reaction addition with proper validation and role management"""
        reaction = payload.emoji
        reaction_str = str(reaction)
        reaction_key = self._get_reaction_key(payload.user_id, payload.message_id, reaction_str)
        
        # Prevent duplicate processing
        if reaction_key in self.processing_reactions:
            return
        self.processing_reactions.add(reaction_key)
        
        if not payload.guild_id:
            return
        
        try:
            # Get guild and validate
            guild = self.client.get_guild(payload.guild_id)
            if not guild:
                try:
                    guild = await self.client.fetch_guild(payload.guild_id)
                except NotFound:
                    return

            # Get user and validate
            user = guild.get_member(payload.user_id)
            if not user:
                try:
                    user = await guild.fetch_member(payload.user_id)
                except NotFound:
                    return
            if user.bot:
                return

            # Get channel and validate
            channel = guild.get_channel(payload.channel_id)
            if not isinstance(channel, TextChannel):
                return

            Logger = Logs.Logger(guild=guild, user=user, cog=self)
            
            # Check if feature is enabled
            feature = await Feature.get_guild_feature_or_none(
                feature_name="reaction_roles", guild_id=guild.id
            )
            if not feature or not feature.enabled:
                return

            # Get reaction role configuration
            reaction_roles = feature.get_setting("reaction_roles", [])
            message_data = await Messages.get(message_id=payload.message_id)
            if not message_data:
                return

            reaction_role = next(
                (rr for rr in reaction_roles if str(rr["message_id"]) == str(message_data.id)),
                None,
            )
            if not reaction_role:
                return

            # Find matching reaction configuration
            reaction_id = reaction.name if reaction.is_unicode_emoji() else str(reaction.id)
            reaction_config = next(
                (
                    r for r in reaction_role["reactions"]
                    if str(r.get("emoji")) == str(reaction_id) or 
                       r.get("url") == str(reaction.url)
                ),
                None,
            )
            if not reaction_config:
                return

            # Get the actual message
            try:
                message = await channel.fetch_message(payload.message_id)
            except NotFound:
                return

            # Get the role
            try:
                role = guild.get_role(int(reaction_config["role_id"]))
                if not role:
                    role = await guild.fetch_role(int(reaction_config["role_id"]))
            except (NotFound, ValueError):
                await Logger.warning(
                    "Role not found or invalid", 
                    context={"role_id": reaction_config["role_id"]}
                )
                return

            # Check if user already has the role (toggle off)
            if role in user.roles:
                if reaction_role.get("allow_unselect", True):
                    await user.remove_roles(role, reason="ReactionRole: Unselected role")
                    
                    embed = Embed.Info(
                        title="Reaction Role",
                        description=f"You have unselected the role: **{role.name}** in {channel.mention}",
                    ).set_author(
                        name=guild.name,
                        icon_url=guild.icon.url if guild.icon else None,
                    ).set_footer(text=f"Guild ID: {guild.id}")
                    
                    await self._send_user_notification(user, embed, Logger)
                else:
                    embed = Embed.Warning(
                        title="Reaction Role",
                        description="You cannot unselect this role",
                    ).set_author(
                        name=guild.name,
                        icon_url=guild.icon.url if guild.icon else None,
                    ).set_footer(text=f"Guild ID: {guild.id}")
                    
                    await self._send_user_notification(user, embed, Logger)

                # Remove reaction if configured
                if reaction_role.get("remove_reactions", True):
                    await self._safe_remove_reaction(message, reaction, user, Logger)
                return

            # User doesn't have role - validate before adding
            can_react, error_message = await self._validate_user_reaction(
                user, reaction_role, guild, channel, message, is_adding=True
            )

            if not can_react:
                embed = Embed.Warning(
                    title="Reaction Role",
                    description=error_message
                ).set_author(
                    name=guild.name,
                    icon_url=guild.icon.url if guild.icon else None,
                ).set_footer(text=f"Guild ID: {guild.id}")
                
                await self._send_user_notification(user, embed, Logger)
                
                await self._safe_remove_reaction(message, reaction, user, Logger)
                return

            # Add the role
            await user.add_roles(role, reason="ReactionRole: Added role")
            
            # Update cooldown
            if reaction_role.get("cooldown"):
                user_key = f"{user.id}_{message.id}"
                self.user_cooldowns[user_key] = time.time()
            
            embed = Embed.Info(
                title="Reaction Role",
                description=f"You have selected the role: **{role.name}** in {channel.mention}",
            ).set_author(
                name=guild.name,
                icon_url=guild.icon.url if guild.icon else None,
            ).set_footer(text=f"Guild ID: {guild.id}")
            
            await self._send_user_notification(user, embed, Logger)
            
            # Remove reaction if configured
            if reaction_role.get("remove_reactions", True):
                await self._safe_remove_reaction(message, reaction, user, Logger)

        finally:
            self.processing_reactions.discard(reaction_key)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """Handle reaction additions"""
        try:
            await self._process_reaction_add(payload)
        except Exception as e:
            logger.error(f"Unexpected error in reaction add handler: {e}", exc_info=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        """Handle reaction removals (only for manual removals, not bot removals)"""
        try:
            reaction_str = str(payload.emoji)
            reaction_key = self._get_reaction_key(payload.user_id, payload.message_id, reaction_str)
            
            # Skip if this was a bot-removed reaction
            if reaction_key in self.bot_removed_reactions:
                self.bot_removed_reactions.discard(reaction_key)
                logger.info("1")
                return
            
            # Prevent duplicate processing
            if reaction_key in self.processing_reactions:
                logger.info("2")
                return
            self.processing_reactions.add(reaction_key)
            
            if not payload.guild_id:
                logger.info("3")
                return
            
            try:
                # Get guild and validate
                guild = self.client.get_guild(payload.guild_id)
                if not guild:
                    try:
                        guild = await self.client.fetch_guild(payload.guild_id)
                    except NotFound:
                        logger.info("4")
                        return

                # Get user and validate
                user = guild.get_member(payload.user_id)
                if not user:
                    try:
                        user = await guild.fetch_member(payload.user_id)
                    except NotFound:
                        logger.info("6")
                        return
                if user.bot:
                    logger.info("5")
                    return

                # Get channel and validate
                channel = guild.get_channel(payload.channel_id)
                if not channel:
                    try:
                        channel = await guild.fetch_channel(payload.channel_id)
                    except NotFound:
                        logger.info("7")
                        return
                if not isinstance(channel, TextChannel):
                    logger.info("8")
                    return

                Logger = Logs.Logger(guild=guild, user=user, cog=self)
                
                # Check if feature is enabled
                feature = await Feature.get_guild_feature_or_none(
                    feature_name="reaction_roles", guild_id=guild.id
                )
                if not feature or not feature.enabled:
                    logger.info("9")
                    return

                # Get reaction role configuration
                reaction_roles = feature.get_setting("reaction_roles", [])
                message_data = await Messages.get(message_id=payload.message_id)
                if not message_data:
                    logger.info("10")
                    return

                reaction_role = next(
                    (rr for rr in reaction_roles if str(rr["message_id"]) == str(message_data.id)),
                    None,
                )
                if not reaction_role:
                    logger.info("11")
                    return

                # Only process if unselect is allowed
                if not reaction_role.get("allow_unselect", True):
                    logger.info("12")
                    return

                # Find matching reaction configuration
                reaction_id = payload.emoji.name if payload.emoji.is_unicode_emoji() else str(payload.emoji.id)
                reaction_config = next(
                    (
                        r for r in reaction_role["reactions"]
                        if str(r.get("emoji")) == str(reaction_id) or 
                           r.get("url") == str(payload.emoji.url)
                    ),
                    None,
                )
                if not reaction_config:
                    logger.info("13")
                    return

                # Get the role
                try:
                    role = guild.get_role(int(reaction_config["role_id"]))
                    if not role:
                        role = await guild.fetch_role(int(reaction_config["role_id"]))
                except (NotFound, ValueError):
                    await Logger.warning(
                        "Role not found or invalid", 
                        context={"role_id": reaction_config["role_id"]}
                    )
                    logger.info("14")
                    return

                # Remove role if user has it
                if role in user.roles:
                    await user.remove_roles(role, reason="ReactionRole: Unselected role (manual removal)")
                    
                    embed = Embed.Info(
                        title="Reaction Role",
                        description=f"You have unselected the role: **{role.name}** in {channel.mention}",
                    ).set_author(
                        name=guild.name,
                        icon_url=guild.icon.url if guild.icon else None,
                    ).set_footer(text=f"Guild ID: {guild.id}")
                    
                    await self._send_user_notification(user, embed, Logger)

            finally:
                self.processing_reactions.discard(reaction_key)
                
        except Exception as e:
            logger.error(f"Unexpected error in reaction remove handler: {e}", exc_info=True)


def setup(client):
    client.add_cog(ReactionRole(client))