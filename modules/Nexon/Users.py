try:
    from .DataManager import DataManager
    from .sidecord import get_name, extract_emojis, info_embed
    from .logger import logger
    from .Badges import BadgeManager, Badge
except: 
    from DataManager import DataManager
from datetime import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Set, Optional, Union
from nextcord import Member, Message, User
from nextcord import Interaction as init, File
from nextcord.ext.application_checks import check
import re
import json
from pathlib import Path
from collections import Counter
from rich.console import Console
from rich.table import Table




@dataclass
class AttachmentTypes:
    images: int = 0
    videos: int = 0
    audio: int = 0
    other: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'AttachmentTypes':
        if isinstance(data, cls):
            return data
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class BotStatistics:
    messages_sent: int = 0
    commands_processed: int = 0
    errors_encountered: int = 0
    features_used: Dict[str, int] = field(default_factory=dict)
    command_errors: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BotStatistics':
        if isinstance(data, cls):
            return data
        return cls(**data)

@dataclass
class UserData:
    # Basic Info
    name: str 
    joined_at: str
    unique_names: Set[str] = field(default_factory=set)
    last_updated: Optional[datetime] = None
    
    # Message Statistics
    total_messages: int = 0
    character_count: int = 0
    word_count: int = 0
    
    # Content Analysis
    attachments_sent: int = 0
    attachment_types: AttachmentTypes = field(default_factory=AttachmentTypes)
    gif_sent: int = 0
    mentions_count: int = 0
    unique_users_mentioned: Set[int] = field(default_factory=set)
    emoji_count: int = 0
    custom_emoji_count: int = 0
    unique_emojis_used: Set[str] = field(default_factory=set)
    unique_custom_emojis_used: Set[str] = field(default_factory=set)
    preferred_channels: Dict[str, int] = field(default_factory=dict)
    
    # Interaction Patterns
    replies_count: int = 0
    reactions_received: int = 0
    reactions_given: int = 0
    
    # Command Usage
    commands_used: int = 0
    favorite_commands: Dict[str, int] = field(default_factory=dict)
    
    # Link Sharing
    links_shared: int = 0
    unique_domains: Set[str] = field(default_factory=set)
    
    # Message Types
    edited_messages: int = 0
    deleted_messages: int = 0
    
    # Special Events
    birthdate: Optional[datetime] = None
    
    # Achievement Tracking
    badges: Set[int] = field(default_factory=set)
    milestones: Dict[str, any] = field(default_factory=dict) #TODO
    reputation: int = 0 #TODO
    
    #Version
    version: int = 1

    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    # Add bot-specific statistics field
    bot_stats: Optional[BotStatistics] = field(default=None)
    
    def set_custom_data(self, key: str, value: Any) -> None:
        """Set a custom data field"""
        self.custom_data[key] = value
        
    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Get a custom data field"""
        return self.custom_data.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        return self.get_custom_data(key)
        
    def __setitem__(self, key: str, value: Any) -> None:
        self.set_custom_data(key, value)
    
    def migrate_user_data(data: dict) -> dict:
        version = data.get('version', 0)  # Default to version 0 if not present
        if version == 0:
            # Migrate from version 0 to version 1
            data['version'] = 1
            if data["badges"]:
                data["badges"] = set()

        # if version == 1:
        #     data['version'] = 2
        #     if 'another_new_field' not in data:
        #         data['another_new_field'] = 'default_value'
        return data
    
    @classmethod
    def from_dict(cls, data: Optional[dict] = None) -> 'UserData':
        """
        Safely create a UserData instance from a dictionary with default values for missing fields.
        """
        if data is None:
            data = {}

        data = data.copy()
        data = cls.migrate_user_data(data)

        # Extract and handle custom data separately
        custom_data = data.pop('custom_data', {})

        # Define defaults for all fields
        defaults = {
            'name': "Unknown",
            'birthdate': None,
            'joined_at': None,
            'last_updated': datetime.now(),
            'unique_users_mentioned': set(),
            'unique_emojis_used': set(),
            'unique_custom_emojis_used': set(),
            'unique_domains': set(),
            'unique_names': set(),
            'badges': set(),
            'favorite_commands': {},
            'preferred_channels': {},
            'milestones': {},
            'attachment_types': AttachmentTypes(),
            'bot_stats': BotStatistics()
        }

        # Process datetime fields
        for field in ['birthdate', 'last_updated']:
            if isinstance(data.get(field), str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = defaults[field]
            elif field not in data:
                data[field] = defaults[field]

        # Process set fields
        set_fields = [
            'unique_users_mentioned', 'unique_emojis_used', 
            'unique_custom_emojis_used', 'unique_domains',
            'unique_names', 'badges'
        ]
        for field in set_fields:
            try:
                data[field] = set(data.get(field, []))
            except (TypeError, ValueError):
                data[field] = set()

        # Process dictionary fields
        dict_fields = ['favorite_commands', 'preferred_channels', 'milestones']
        for field in dict_fields:
            if not isinstance(data.get(field), dict):
                data[field] = {}

        # Handle complex objects
        if 'attachment_types' in data:
            if isinstance(data['attachment_types'], dict):
                try:
                    data['attachment_types'] = AttachmentTypes.from_dict(data['attachment_types'])
                except (ValueError, TypeError):
                    data['attachment_types'] = AttachmentTypes()
            elif not isinstance(data['attachment_types'], AttachmentTypes):
                data['attachment_types'] = AttachmentTypes()
        else:
            data['attachment_types'] = AttachmentTypes()

        if 'bot_stats' in data:
            if isinstance(data['bot_stats'], dict):
                try:
                    data['bot_stats'] = BotStatistics.from_dict(data['bot_stats'])
                except (ValueError, TypeError):
                    data['bot_stats'] = BotStatistics()
            elif not isinstance(data['bot_stats'], BotStatistics):
                data['bot_stats'] = BotStatistics()
        else:
            data['bot_stats'] = BotStatistics()

        # Create instance with processed data
        instance = cls(**{k: data.get(k, v) for k, v in defaults.items()})
        instance.custom_data = custom_data
        return instance

    def to_dict(self) -> dict:
        data = {
            # Basic Info
            "name": self.name,
            "joined_at": self.joined_at,
            "unique_names": list(self.unique_names),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            
            # Message Statistics
            "total_messages": self.total_messages,
            "character_count": self.character_count,
            "word_count": self.word_count,
            
            # Content Analysis
            "attachments_sent": self.attachments_sent,
            "attachment_types": self.attachment_types.to_dict(),
            "gif_sent": self.gif_sent,
            "mentions_count": self.mentions_count,
            "unique_users_mentioned": list(self.unique_users_mentioned),
            "emoji_count": self.emoji_count,
            "custom_emoji_count": self.custom_emoji_count,
            "unique_emojis_used": list(self.unique_emojis_used),
            "unique_custom_emojis_used": list(self.unique_custom_emojis_used),
            
            # Interaction Patterns
            "replies_count": self.replies_count,
            "reactions_received": self.reactions_received,
            "reactions_given": self.reactions_given,
            
            # Command Usage
            "commands_used": self.commands_used,
            "favorite_commands": self.favorite_commands,
            
            # Link Sharing
            "links_shared": self.links_shared,
            "unique_domains": list(self.unique_domains),
            
            # Message Types
            "edited_messages": self.edited_messages,
            "deleted_messages": self.deleted_messages,
            
            # Special Events
            "birthdate": self.birthdate.isoformat() if self.birthdate else None,
            
            # Preferences
            "preferred_channels": self.preferred_channels,
            
            # Achievement Tracking
            "badges": list(self.badges),
            "milestones": self.milestones,
            "reputation": self.reputation,
            
            #Version
            'version': self.version,
            
            # Bot Statistics
            "bot_stats": self.bot_stats.to_dict() if self.bot_stats else None
        }
        data['custom_data'] = self.custom_data
        return data

    @classmethod
    def from_member(cls, member: Member) -> 'UserData':
        return cls(
            name=get_name(member),
            joined_at=str(member.created_at),
            last_updated=datetime.now()
        )


class UserManager(DataManager):
    def __init__(self, user: Union[User, Member]):
        # Initialize with user-specific file and UserData as default
        super().__init__(
            name="Users",
            file=str(user.id),
            default=UserData.from_member(user).to_dict(),
            entity_type="Users",
            addNameFolder=False
        )
        self.badgeManager = BadgeManager(self)
        self.user_id = user.id
        # Convert loaded data to UserData object
        self._user_data: UserData = self._load_user_data()

    def _load_user_data(self) -> UserData:
        """Convert raw data to UserData object"""
        return UserData.from_dict(self.data)

    def save(self) -> None:
        """Save UserData to JSON file"""
        self.data = self._user_data.to_dict()
        super().save()
    
    def load(self) -> UserData:
        """Load JSON file and return as UserData object"""
        super().load()
        self._user_data = self._load_user_data()
        return self._user_data
    def delete(self):
        """Deletes the user data"""
        return super().delete(None)

    @property
    def user_data(self) -> UserData:
        """Access the UserData object"""
        return self._user_data
    
    def generalUpdateInfo(self, user: Member | User):
        if get_name(user) == self.user_data.name:
            return
        else:
            self.user_data.unique_names.add(self.user_data.name)
            self.user_data.name = get_name(user)
            self.user_data.last_updated = datetime.now()
            return self.save()
    
    async def BadgeDetect(self, message: Union[Message, init]) -> None:
        """
        Checks for new badges and sends notifications to user.
        Args:
            message: Discord message object or boolean for command-based checks
        """
        try:
            # Get newly earned badges
            new_badges:List[Badge] = await self.badgeManager.check_badges(message)
            
            # Skip if no new badges earned
            if not new_badges:
                return

            # Create notification embed for each new badge
            for badge in new_badges:
                embed = info_embed(
                    title=f"🏆 New Badge Earned: {badge.title}!",
                    description=badge.description
                )
                
                if badge.image_path and Path(badge.image_path).exists():
                    file = File(badge.image_path, filename="thumbnail.jpg")
                    embed.set_thumbnail(url=f"attachment://thumbnail.jpg")
                    
                embed.add_field(
                    name="Unlocked",
                    value=f"<t:{int(datetime.now().timestamp())}:R>",
                    inline=False
                )
                
                # Try to DM the user
                try:
                    if isinstance(message, Message):
                        await message.author.send(embed=embed, file=file)
                    elif isinstance(message, init):
                        await message.user.send(embed=embed, file=file)
                except Exception as e:
                    if isinstance(message, Message):
                        await message.reply(embed=embed, file=file)
                    elif isinstance(message, init):
                        await message.send(embed=embed, ephemeral=True, file=file)
                    
            # Save badge progress
            self.save()
            
        except Exception as e:
            logger.error(f"Error in BadgeDetect: {str(e)}")
    
    async def incrementMessageCount(self, message: Message):
        self.generalUpdateInfo(message.author)
        await self.BadgeDetect(message)
        # await self.BadgeDetect(False)
        content = message.content
        self.user_data.total_messages += 1
        self.user_data.character_count += len(content.replace(" ", ""))
        self.user_data.word_count += len(content.split())
        self.user_data.preferred_channels[str(message.channel.id)] = \
            self.user_data.preferred_channels.get(str(message.channel.id), 0) + 1

        self.user_data.attachments_sent += len(message.attachments)
        if len(message.attachments) >= 1:
            for att in message.attachments:
                if att.content_type and (
                    att.content_type.startswith("image") or
                    att.content_type.startswith("video") or  
                    att.content_type.startswith("audio")
                ):
                    media_type = att.content_type.split('/')[0]
                    if media_type == 'image':
                        self.user_data.attachment_types.images += 1
                    elif media_type == 'video':
                        self.user_data.attachment_types.videos += 1
                    elif media_type == 'audio':
                        self.user_data.attachment_types.audio += 1
                else:
                    self.user_data.attachment_types.other += 1
        mentions = re.findall(r"<@(\d+)>", content)
        self.user_data.mentions_count += len(mentions)
        self.user_data.unique_users_mentioned.update(mentions)
        #<a:dddd:706660674780266536>
        emojis = extract_emojis(content)
        self.user_data.emoji_count += len(emojis)
        self.user_data.unique_emojis_used.update(emojis)
        customEmojis = re.findall(r"<a?:[a-zA-Z0-9_]+:(\d+)>", content)
        self.user_data.custom_emoji_count += len(customEmojis)
        self.user_data.unique_custom_emojis_used.update(customEmojis)
        self.user_data.replies_count += 1 if message.reference else 0
        links = re.findall(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", content)
        self.user_data.links_shared += len(links)
        self.user_data.unique_domains.update(links)
        gifs = re.findall(r'https?://tenor\.com/\S+', content)
        self.user_data.gif_sent += len(gifs)
        
        self.save()
    
    def increment_command_count(self, command_name: str) -> None:
        """Increment the command usage count"""
        
        self._user_data.commands_used += 1
        self._user_data.favorite_commands[command_name] = \
            self._user_data.favorite_commands.get(command_name, 0) + 1
        self.save()

    @classmethod
    async def commandCount(self, ctx: init):
        """Command track usage"""
        # Get or create UserManager instance for the command user
        user_manager = UserManager(ctx.user)
        user_manager.generalUpdateInfo(ctx.user)
        # Track command usage
        try:
            command_name = ctx.application_command.name
            user_manager.increment_command_count(command_name)
            await self.BadgeDetect(user_manager, ctx)
        except:
            pass

    
    def init_bot_stats(self):
        """Initialize bot statistics if not present"""
        if not self.user_data.bot_stats:
            self.user_data.bot_stats = BotStatistics()
            self.save()

    def record_bot_message(self):
        """Record a message sent by the bot"""
        self.init_bot_stats()
        self.user_data.bot_stats.messages_sent += 1
        self.save()

    def record_command_processed(self, command_name: str):
        """Record a processed command"""
        self.init_bot_stats()
        self.user_data.bot_stats.commands_processed += 1
        self.user_data.bot_stats.features_used[command_name] = \
            self.user_data.bot_stats.features_used.get(command_name, 0) + 1
        self.save()

    def record_error(self, command_name: str, error_message: str):
        """Record an error that occurred"""
        self.init_bot_stats()
        self.user_data.bot_stats.errors_encountered += 1
        if command_name not in self.user_data.bot_stats.command_errors:
            self.user_data.bot_stats.command_errors[command_name] = []
        self.user_data.bot_stats.command_errors[command_name].append(error_message)
        self.save()

    def get_bot_stats_summary(self) -> dict:
        """Get a summary of bot statistics"""
        if not self.user_data.bot_stats:
            return {}
            
        stats = self.user_data.bot_stats
        return {
            "messages_sent": stats.messages_sent,
            "commands_processed": stats.commands_processed,
            "errors": stats.errors_encountered,
            "top_features": dict(sorted(
                stats.features_used.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
        }
    
    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to UserData object"""
        if hasattr(self._user_data, name):
            return getattr(self._user_data, name)
        raise AttributeError(f"'UserManager' object has no attribute '{name}'")


def load_json_files(directory):
    """Load all JSON files from a directory."""
    data = []
    for file in Path(directory).glob("*.json"):
        with open(file, "r", encoding='utf-8') as f:
            data.append(json.load(f))
    return data

def analyze_data(data):
    """Analyze the loaded data."""
    total_users = len(data)
    total_messages = sum(user["total_messages"] for user in data)
    total_words = sum(user["word_count"] for user in data)
    total_reactions_received = sum(user["reactions_received"] for user in data)
    total_reactions_given = sum(user["reactions_given"] for user in data)
    total_mentions = sum(user["mentions_count"] for user in data)
    
    # Activity metrics
    total_attachments = sum(user["attachments_sent"] for user in data)
    attachment_types = Counter(
        {key: 0 for key in ["images", "videos", "audio", "other"]}
    )
    for user in data:
        attachment_types.update(user["attachment_types"])
    
    # Command usage
    command_usage = Counter()
    for user in data:
        command_usage.update(user["favorite_commands"])
    
    # Preferred channels
    preferred_channels = Counter()
    for user in data:
        preferred_channels.update(user["preferred_channels"])
    
    # Domain analysis
    unique_domains = set()
    for user in data:
        unique_domains.update(user["unique_domains"])

    # Badge distribution
    badges = Counter()
    for user in data:
        badges.update(user["badges"])
    
    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "total_words": total_words,
        "total_reactions_received": total_reactions_received,
        "total_reactions_given": total_reactions_given,
        "total_mentions": total_mentions,
        "total_attachments": total_attachments,
        "attachment_types": dict(attachment_types),
        "top_commands": command_usage.most_common(10),
        "top_channels": preferred_channels.most_common(10),
        "unique_domains_count": len(unique_domains),
        "unique_domains": list(unique_domains),
        "badge_distribution": dict(badges),
    }

def format_report(stats):
    """Format the analytics report using rich."""
    console = Console()

    # Create a table for better visualization
    table = Table(title="Analytics Report")
    
    table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="magenta")
    
    table.add_row("Total Users", str(stats["total_users"]))
    table.add_row("Total Messages", str(stats["total_messages"]))
    table.add_row("Total Words", str(stats["total_words"]))
    table.add_row("Reactions Received", str(stats["total_reactions_received"]))
    table.add_row("Reactions Given", str(stats["total_reactions_given"]))
    table.add_row("Total Mentions", str(stats["total_mentions"]))
    table.add_row("Total Attachments", str(stats["total_attachments"]))
    
    table.add_row("Attachment Types", str(stats["attachment_types"]))
    table.add_row("Top Commands", str(stats["top_commands"]))
    table.add_row("Top Channels", str(stats["top_channels"]))
    table.add_row("Unique Domains", str(stats["unique_domains_count"]))
    table.add_row("Badge Distribution", str(stats["badge_distribution"]))
    
    # Display the table
    console.print(table)

def format_for_discord(stats):
    """Format the analytics as a string suitable for a Discord message."""
    formatted = (
        f"**Analytics Report**\n"
        f"**Total Users:** {stats['total_users']}\n"
        f"**Total Messages:** {stats['total_messages']}\n"
        f"**Total Words:** {stats['total_words']}\n"
        f"**Reactions Received:** {stats['total_reactions_received']}\n"
        f"**Reactions Given:** {stats['total_reactions_given']}\n"
        f"**Total Mentions:** {stats['total_mentions']}\n"
        f"**Total Attachments:** {stats['total_attachments']}\n"
        f"**Attachment Types:** {stats['attachment_types']}\n"
        f"**Top Commands:** {stats['top_commands']}\n"
        f"**Top Channels:** {stats['top_channels']}\n"
        f"**Unique Domains Count:** {stats['unique_domains_count']}\n"
        f"**Badge Distribution:** {stats['badge_distribution']}\n"
    )
    return f"```{formatted}```"

if __name__ == "__main__":
    import os
    os.system("cls")
    directory = "Data/Users/"
    data = load_json_files(directory)
    stats = analyze_data(data)
    
    # Print rich table to console
    format_report(stats)
