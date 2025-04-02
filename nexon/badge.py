"""
nexon.badge
~~~~~~~~~~

Badge system implementation for tracking user achievements.

:copyright: (c) 2025 Mahirox36
:license: MIT, see LICENSE for more details.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Union, Callable
from typing import List, Optional
from datetime import datetime, timedelta


from .enums import RequirementType, Rarity, ComparisonType
import re
from .utils import extract_emojis
from .message import Message
from .interactions import Interaction
from .data.user import UserData
from tortoise.expressions import Q
from .data.models import UserBadge, Badge, BadgeRequirement

if TYPE_CHECKING:
    from .user import User
    from .guild import Guild
    from .member import Member

from .database import DataManager
import logging
logger = logging.getLogger(__name__)

__all__ = (
    "BadgeManager",
    "onBadgeEarned",
)


async def onBadgeEarned(user: Union['User', 'Member'], badge: 'Badge') -> None:
    """Default event handler called when a user earns a badge.
    
    .. versionadded:: Nexon 0.2.3
    
    Parameters
    ----------
    badge: :class:`Badge`
        The badge that was earned
    user: Union[:class:`User`, :class:`Member`]
        The user who earned the badge
    """
    # Suppress unused parameter warnings
    _ = (badge, user)

class BadgeManager:
    """Manages the badge system for tracking user achievements.

    .. versionadded:: Nexon 0.2.3

    Parameters
    -----------
    guild_id: Optional[:class:`int`]
        The guild ID if this manager is for a specific guild
    """
    badge_earned_callback = staticmethod(onBadgeEarned)
    
    def __init__(self, guild_id: Optional[int] = None):
        self.guild_id = guild_id
    
    @classmethod
    def set_badge_earned_callback(cls, callback: Callable) -> None:
        """Set a new callback function for badge earning events"""
        cls.badge_earned_callback = staticmethod(callback)
    
    @classmethod
    async def guild_has_badges(cls, guild_id: int) -> bool:
        return await Badge.filter(guild_id=guild_id).exists()

    @classmethod
    def try_get_guild(cls, guild: Optional['Guild']) -> BadgeManager:
        """Try to get a guild object by its ID. and if didn't get it, it get the global one"""
        return cls(guild.id) if guild else cls()
    
    async def create_badge(self,
                           name: str,
                           description: str,
                           icon_url: str,
                           emoji: str,
                           rarity: Rarity = Rarity.common,
                           hidden: bool = False,
                           requirements: Optional[list[tuple[RequirementType, ComparisonType, str]]] = None
                           ) -> Badge:
        badge = await Badge.create_badge_with_requirements(
            name=name,
            description=description,
            icon_url=icon_url,
            emoji=emoji,
            guild_id=self.guild_id,
            rarity=rarity,
            hidden=hidden,
            requirements=requirements
        )
        return badge

    async def delete_badge(self, badge_id: int) -> bool:
        badge = await Badge.filter(id=badge_id).delete()
        return badge > 0

    async def get_badge(self, badge_id: int) -> Optional[Badge]:
        return await Badge.get_or_none(id=badge_id)

    async def get_all_badges(self) -> List[Badge]:
        query = Badge.filter(guild_id=self.guild_id if self.guild_id is not None else None)
        return await query.all()

    async def update_badge(self, badge_id: int, **kwargs) -> Optional[Badge]:
        """Update a badge's attributes in the database.

        Parameters
        ----------
        badge_id: int
            The ID of the badge to update
        **kwargs
            The attributes to update. Can include:
            - name: str
            - description: str 
            - icon_url: str
            - emoji: str
            - rarity: Rarity
            - hidden: bool
            - requirements: List[tuple[RequirementType, ComparisonType, str]]

        Returns
        -------
        Optional[Badge]
            The updated badge, or None if badge not found
        """
        badge = await self.get_badge(badge_id)
        if not badge:
            return None

        if 'requirements' in kwargs:
            # Delete existing requirements
            await BadgeRequirement.filter(badge_id=badge_id).delete()
            # Create new requirements
            requirements = kwargs.pop('requirements')
            if requirements:
                await BadgeRequirement.bulk_create([
                    BadgeRequirement(
                        badge=badge,
                        type=req[0],
                        comparison_type=req[1],
                        value=req[2]
                    ) for req in requirements
                ])

        # Update other badge attributes
        await Badge.filter(id=badge_id).update(**kwargs)
        return await self.get_badge(badge_id)

    async def award_badge(self, user: Union['User', 'Member'], badge_id: int) -> bool:
        if await UserBadge.filter(user_id=user.id, badge_id=badge_id).exists():
            return False  # Already has the badge
        await UserBadge.create(user_id=user.id, badge_id=badge_id)
        # await Tortoise.get_connection("default").execute_query("COMMIT")  # Ensure changes are saved
        badge = await self.get_badge(badge_id)
        if not badge:
            raise RuntimeError("Badge creation succeeded but fetching failed, which is unexpected.")
        await self.badge_earned_callback(user, badge)
        return True

    async def remove_user_badge(self, user_id: int, badge_id: int) -> bool:
        deleted_count = await UserBadge.filter(user_id=user_id, badge_id=badge_id).delete()
        return deleted_count > 0

    async def get_user_badges(self, user_id: int) -> List[UserBadge]:
        return await UserBadge.filter(user_id=user_id).prefetch_related("badge").all()

    async def get_user_unowned_badges(self, user_id: int) -> List[Badge]:
        owned_badge_ids = await UserBadge.filter(user_id=user_id).values_list("badge_id", flat=True)
        return await Badge.filter(Q(id__in=owned_badge_ids)).all()

    async def get_user_hidden_badges(self, user_id: int) -> List[Badge]:
        owned_badge_ids = await UserBadge.filter(user_id=user_id).values_list("badge_id", flat=True)
        return await Badge.filter(Q(id__in=owned_badge_ids) & Q(hidden=True)).all()

    async def verify_requirement(
        self, 
        requirement: BadgeRequirement, 
        user_data: 'UserData',
        context: Optional[Union[Message, Interaction]] = None
    ) -> bool:
        """Verify if a single requirement is met.
        
        Args:
            requirement: Badge requirement to verify
            user_data: User data containing stats
            context: Optional message or interaction context
            
        Returns:
            bool: Whether requirement is met
        """
        logger.debug(f"Verifying requirement: {requirement.type} for user {getattr(user_data, 'id', 'Unknown')}")
        
        # Create dispatch table for basic numeric requirements
        basic_requirements = {
            RequirementType.MESSAGE_COUNT: lambda: requirement.compare(user_data.total_messages),
            RequirementType.REACTION_RECEIVED: lambda: requirement.compare(user_data.reactions_received_count),
            RequirementType.REACTION_GIVEN: lambda: requirement.compare(user_data.reactions_given_count), 
            RequirementType.ATTACHMENT_COUNT: lambda: requirement.compare(user_data.attachment_count),
            RequirementType.MENTION_COUNT: lambda: requirement.compare(user_data.mention_count),
            RequirementType.LINK_SHARED: lambda: requirement.compare(user_data.links_count),
            RequirementType.GIF_COUNT: lambda: requirement.compare(user_data.gif_count),
            RequirementType.MESSAGE_DELETE_COUNT: lambda: requirement.compare(user_data.deleted_messages_count),
            RequirementType.MESSAGE_EDIT_COUNT: lambda: requirement.compare(user_data.edited_messages_count),
            RequirementType.UNIQUE_EMOJI_COUNT: lambda: requirement.compare(
                len(user_data.unique_emojis_used) + len(user_data.unique_custom_emojis_used)
            ),
            RequirementType.CHANNEL_ACTIVITY: lambda: requirement.compare(
                user_data.preferred_channels.get(requirement.value, 0)
            ),
            RequirementType.COMMAND_USE: lambda: requirement.compare(
                user_data.favorites_commands.get(requirement.value.lower(), 0)
            )
        }

        # Check basic requirements first
        if requirement.type in basic_requirements:
            return basic_requirements[requirement.type]()

        # Handle time-based requirements
        if requirement.type == RequirementType.TIME_BASED:
            try:
                time_str = requirement.value.strip().upper()
                current_time = datetime.now()
                hour, minute = map(int, time_str.replace(' ', ':').split(':')[:2])
                
                if 'PM' in time_str and hour != 12:
                    hour += 12
                elif 'AM' in time_str and hour == 12:
                    hour = 0

                current_minutes = current_time.hour * 60 + current_time.minute
                target_minutes = hour * 60 + minute
                return requirement.compare(current_minutes, target_minutes)
            except (ValueError, AttributeError):
                return False

        # Handle inactive duration
        if requirement.type == RequirementType.INACTIVE_DURATION:
            return (user_data.last_message is not None and 
                   user_data.last_message + timedelta(hours=float(requirement.value)) < datetime.now())

        # Context-dependent requirements
        if not context:
            return False

        if isinstance(context, Message):
            message_requirements = {
                RequirementType.CONTENT_MATCH: lambda: self._check_content_match(context.content, requirement.value),
                RequirementType.CONTENT_LENGTH: lambda: requirement.compare(len(context.content)),
                RequirementType.MESSAGE_SENT: lambda: True,
                RequirementType.SPECIFIC_EMOJI: lambda: any(emoji in context.content for emoji in extract_emojis(requirement.value)),
                RequirementType.GIF_SENT: lambda: requirement.compare(len(re.findall(
                    r'https?://[^\s]+\.(gif|mp4)|https?://(tenor\.com|gfycat\.com)/[^\s]+', 
                    context.content
                ))),
                RequirementType.ATTACHMENT_SENT: lambda: requirement.compare(len(context.attachments)),
                RequirementType.UNIQUE_MENTION_COUNT: lambda: requirement.compare(len(user_data.unique_users_mentioned)),
                RequirementType.EMOJI_USED: lambda: requirement.compare(len(re.findall(
                    r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF\u2700-\u27BF]', 
                    context.content
                ))),
                RequirementType.CUSTOM_EMOJI_USED: lambda: requirement.compare(len(re.findall(r'<:\w+:\d+>', context.content)))
            }

            if requirement.type in message_requirements:
                return message_requirements[requirement.type]()

            # Special case for user interaction
            if requirement.type == RequirementType.SPECIFIC_USER_INTERACTION:
                if not (context.reference and context.reference.message_id):
                    return False
                referenced_msg = (context.reference.cached_message or 
                                await context.channel.fetch_message(context.reference.message_id))
                return str(referenced_msg.author.id) == requirement.value

        elif isinstance(context, Interaction) and requirement.type == RequirementType.ALL_COMMANDS:
            return len(context.client.application_commands) == len(user_data.favorites_commands)

        return False

    def _check_content_match(self, content: str, pattern: str) -> bool:
        """Helper function to check content matching."""
        if not pattern:
            return False
        try:
            return bool(re.compile(pattern, re.IGNORECASE).search(content.lower()))
        except re.error:
            return pattern.lower() in content.lower()

    async def check_for_new_badges(
        self,
        user: Union['User', 'Member'],
        context: Optional[Union[Message, Interaction]] = None
    ) -> List[Badge]:
        """Check if the user has earned any new badges and award them"""
        logger.debug(f"Checking for new badges for user {user.id}")
        unowned_badges = await self.get_user_unowned_badges(user.id)
        earned_badges = []
        userData, _ = await UserData.get_or_create_user(user)
        
        for badge in unowned_badges:
            if not badge.requirements:
                continue
            all_requirements_met = True
            for requirement in badge.requirements:
                if not await self.verify_requirement(requirement, userData, context):
                    all_requirements_met = False
                    break
            if all_requirements_met:
                earned_badges.append(badge)
        
        return earned_badges

    async def check_and_award_badges(
        self,
        user: Union['User', 'Member'],
        context: Optional[Union[Message, Interaction]] = None
    ) -> List[Badge]:
        """Check and award badges to the user"""
        logger.debug(f"Checking and awarding badges for user {user.id}")
        earned_badges = await self.check_for_new_badges(user, context)
        
        for badge in earned_badges:
            await self.award_badge(user, badge.id)
            logger.info(f"Badge {badge.name} awarded to user {user.id}")
        
        return earned_badges