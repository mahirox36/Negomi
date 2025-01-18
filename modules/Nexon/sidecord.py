import asyncio
import time
from typing import Dict, List, Optional, Union, NewType

import emoji
from modules.Nexon import *
from nextcord import ApplicationCheckFailure, DMChannel, Embed, Guild, Member, PermissionOverwrite, Interaction as init, Permissions, Thread, User, Client, TextChannel, VoiceChannel
from nextcord.ext import commands
from nextcord.ext.application_checks import check
from nextcord.errors import ApplicationCheckFailure
from .DataManager import DataManager
from .config import colors, overwriteOwner
from .logger import logger

url = NewType("url", str)

def PermissionOverwriteWith(create_instant_invite: Optional[bool]= None,kick_members: Optional[bool]= None,ban_members: Optional[bool]= None,administrator: Optional[bool]= None,manage_channels: Optional[bool]= None,manage_guild: Optional[bool]= None,add_reactions: Optional[bool]= None,view_audit_log: Optional[bool]= None,priority_speaker: Optional[bool]= None,stream: Optional[bool]= None,read_messages: Optional[bool]= None,view_channel: Optional[bool]= None,send_messages: Optional[bool]= None,send_tts_messages: Optional[bool]= None,manage_messages: Optional[bool]= None,embed_links: Optional[bool]= None,attach_files: Optional[bool]= None,read_message_history: Optional[bool]= None,mention_everyone: Optional[bool]= None,external_emojis: Optional[bool]= None,use_external_emojis: Optional[bool]= None,view_guild_insights: Optional[bool]= None,connect: Optional[bool]= None,speak: Optional[bool]= None,mute_members: Optional[bool]= None,deafen_members: Optional[bool]= None,move_members: Optional[bool]= None,use_voice_activation: Optional[bool]= None,change_nickname: Optional[bool]= None,manage_nicknames: Optional[bool]= None,manage_roles: Optional[bool]= None,manage_permissions: Optional[bool]= None,manage_webhooks: Optional[bool]= None,manage_emojis: Optional[bool]= None,manage_emojis_and_stickers: Optional[bool]= None,use_slash_commands: Optional[bool]= None,request_to_speak: Optional[bool]= None,manage_events: Optional[bool]= None,manage_threads: Optional[bool]= None,create_public_threads: Optional[bool]= None,create_private_threads: Optional[bool]= None,send_messages_in_threads: Optional[bool]= None,external_stickers: Optional[bool]= None,use_external_stickers: Optional[bool]= None,start_embedded_activities: Optional[bool]= None,moderate_members: Optional[bool]= None):
    return PermissionOverwrite(create_instant_invite= create_instant_invite,kick_members= kick_members,ban_members= ban_members,administrator= administrator,manage_channels= manage_channels,manage_guild= manage_guild,add_reactions= add_reactions,view_audit_log= view_audit_log,priority_speaker= priority_speaker,stream= stream,read_messages= read_messages,view_channel= view_channel,send_messages= send_messages,send_tts_messages= send_tts_messages,manage_messages= manage_messages,embed_links= embed_links,attach_files= attach_files,read_message_history= read_message_history,mention_everyone= mention_everyone,external_emojis= external_emojis,use_external_emojis= use_external_emojis,view_guild_insights= view_guild_insights,connect= connect,speak= speak,mute_members= mute_members,deafen_members= deafen_members,move_members= move_members,use_voice_activation= use_voice_activation,change_nickname= change_nickname,manage_nicknames= manage_nicknames,manage_roles= manage_roles,manage_permissions= manage_permissions,manage_webhooks= manage_webhooks,manage_emojis= manage_emojis,manage_emojis_and_stickers= manage_emojis_and_stickers,use_slash_commands= use_slash_commands,request_to_speak= request_to_speak,manage_events= manage_events,manage_threads= manage_threads,create_public_threads= create_public_threads,create_private_threads= create_private_threads,send_messages_in_threads= send_messages_in_threads,external_stickers= external_stickers,use_external_stickers= use_external_stickers,start_embedded_activities= start_embedded_activities,moderate_members= moderate_members)
def PermissionsWith(create_instant_invite: Optional[bool]= None,kick_members: Optional[bool]= None,ban_members: Optional[bool]= None,administrator: Optional[bool]= None,manage_channels: Optional[bool]= None,manage_guild: Optional[bool]= None,add_reactions: Optional[bool]= None,view_audit_log: Optional[bool]= None,priority_speaker: Optional[bool]= None,stream: Optional[bool]= None,read_messages: Optional[bool]= None,view_channel: Optional[bool]= None,send_messages: Optional[bool]= None,send_tts_messages: Optional[bool]= None,manage_messages: Optional[bool]= None,embed_links: Optional[bool]= None,attach_files: Optional[bool]= None,read_message_history: Optional[bool]= None,mention_everyone: Optional[bool]= None,external_emojis: Optional[bool]= None,use_external_emojis: Optional[bool]= None,view_guild_insights: Optional[bool]= None,connect: Optional[bool]= None,speak: Optional[bool]= None,mute_members: Optional[bool]= None,deafen_members: Optional[bool]= None,move_members: Optional[bool]= None,use_voice_activation: Optional[bool]= None,change_nickname: Optional[bool]= None,manage_nicknames: Optional[bool]= None,manage_roles: Optional[bool]= None,manage_permissions: Optional[bool]= None,manage_webhooks: Optional[bool]= None,manage_emojis: Optional[bool]= None,manage_emojis_and_stickers: Optional[bool]= None,use_slash_commands: Optional[bool]= None,request_to_speak: Optional[bool]= None,manage_events: Optional[bool]= None,manage_threads: Optional[bool]= None,create_public_threads: Optional[bool]= None,create_private_threads: Optional[bool]= None,send_messages_in_threads: Optional[bool]= None,external_stickers: Optional[bool]= None,use_external_stickers: Optional[bool]= None,start_embedded_activities: Optional[bool]= None,moderate_members: Optional[bool]= None):
    return Permissions(create_instant_invite= create_instant_invite,kick_members= kick_members,ban_members= ban_members,administrator= administrator,manage_channels= manage_channels,manage_guild= manage_guild,add_reactions= add_reactions,view_audit_log= view_audit_log,priority_speaker= priority_speaker,stream= stream,read_messages= read_messages,view_channel= view_channel,send_messages= send_messages,send_tts_messages= send_tts_messages,manage_messages= manage_messages,embed_links= embed_links,attach_files= attach_files,read_message_history= read_message_history,mention_everyone= mention_everyone,external_emojis= external_emojis,use_external_emojis= use_external_emojis,view_guild_insights= view_guild_insights,connect= connect,speak= speak,mute_members= mute_members,deafen_members= deafen_members,move_members= move_members,use_voice_activation= use_voice_activation,change_nickname= change_nickname,manage_nicknames= manage_nicknames,manage_roles= manage_roles,manage_permissions= manage_permissions,manage_webhooks= manage_webhooks,manage_emojis= manage_emojis,manage_emojis_and_stickers= manage_emojis_and_stickers,use_slash_commands= use_slash_commands,request_to_speak= request_to_speak,manage_events= manage_events,manage_threads= manage_threads,create_public_threads= create_public_threads,create_private_threads= create_private_threads,send_messages_in_threads= send_messages_in_threads,external_stickers= external_stickers,use_external_stickers= use_external_stickers,start_embedded_activities= start_embedded_activities,moderate_members= moderate_members)

owner: Optional[User] = None

def get_name(user:Member):
    return user.global_name if user.global_name else user.display_name

def everyone(guild:Guild):
    return guild.default_role

def debug_embed(
    description: str = None,
    title: str = "Debug",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colors.Debug.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def info_embed(
    description: str = None,
    title: str = "Info",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colors.Info.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def warn_embed(
    description: str = None,
    title: str = "Warning",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colors.Warn.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    embed.set_author
    return embed

def error_embed(
    description: str = None,
    title: str = "Error",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colors.Error.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

class SlashCommandOnCooldown(ApplicationCheckFailure):
    def __init__(self, time_left: float):
        self.time_left = time_left
        super().__init__(f"Command is on cooldown. Try again in {time_left:.2f} seconds.")

# def setup_hybrid(bot: commands.Bot):
#     """
#     Register commands on the bot instance.
#     """
#     def hybrid(name: str, description: str, aliases: List[str] = [], **kwargs: Any):
#         def decorator(func: Callable[..., Any]):
#             # Register text command
#             bot.add_command(commands.Command(func, name="_"+name, **kwargs))
            
#             # Register slash command
#             bot.slash_command(name=name, description=description)(func)
            
#             return func
#         return decorator
    
#     return hybrid

def contains_emoji(text: str) -> bool:
    """
    Check if a string contains any emojis.
    """
    return any(char in emoji.EMOJI_DATA for char in text)
def extract_emojis(text: str) -> list:
    """
    Extract all emojis from a string.
    """
    return [char for char in text if char in emoji.EMOJI_DATA]

async def HaveHigherRole(ctx:init,user:Member):
    if user.top_role.position >= ctx.user.top_role.position:
        await ctx.send(f"User {user} Is Higher Than you")
        return True
    return False

class ApplicationNotOwnerGuild(ApplicationCheckFailure):
    def __init__(self,user:Member,guild:Guild) -> None:
        super().__init__()
        self.guild= guild.name
        self.user= get_name(user)


cooldowns= {}
def cooldown(cooldown_time: int):
    async def predicate(ctx: init) -> bool:
        global cooldowns
        name = ctx.application_command.name
        user_id = ctx.user.id

        if name not in cooldowns:
            cooldowns[name] = {}

        # Check if the user is on cooldown
        if user_id in cooldowns[name]:
            time_left = cooldowns[name][user_id] - time.time()
            if time_left > 0:
                raise SlashCommandOnCooldown(time_left)

        # Set a new cooldown for the user
        cooldowns[name][user_id] = time.time() + cooldown_time
        return True

    return check(predicate)

def is_owner_guild():
    async def predicate(ctx: init) -> bool:

        if not ctx.guild.owner.id == ctx.user.id:
            raise ApplicationNotOwnerGuild(ctx.user,ctx.guild)
        return True

    return check(predicate)

class FeatureDisabled(commands.CheckFailure):
    def __init__(self, message: str, feature_name: str, send_error: bool = True):
        self.message = message
        self.feature_name = feature_name
        self.send_error = send_error
        super().__init__(message)

def remove_numbers(text: str) -> str:
    """Remove numbers from a string."""
    return ''.join(char for char in text if not char.isdigit())

def get_feature_state(guild_id: int) -> List[str]:
    """Get the list of disabled features for a guild."""
    with DataManager("Feature", guild_id, default=[], auto_save=False) as file:
        return file.data

def feature():
    """
    Decorator to check if a feature is enabled.
    Raises FeatureDisabled if the feature is disabled.
    """
    def predicate(ctx):
        # Skip check in DMs
        if not getattr(ctx, 'guild', None):
            return True

        # Get the cog name without numbers
        if hasattr(ctx, 'application_command'):
            # For slash commands
            cog_name = remove_numbers(ctx.application_command.parent_cog.__class__.__name__)
        else:
            # For regular commands
            cog_name = remove_numbers(ctx.cog.__class__.__name__)

        disabled_features = get_feature_state(ctx.guild.id)
        
        if cog_name.lower() in disabled_features:
            raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name
            )
        
        return True

    return check(predicate)

async def check_feature_inside(guild_id: int, cog: object, send_Error: bool = False) -> bool:
    """
    Check if a feature is enabled within other code.
    Returns True if feature is enabled, False if disabled.
    """
    try:
        cog_name = remove_numbers(cog.__class__.__name__.lower())
        disabled_features = get_feature_state(guild_id)
        if cog_name in disabled_features:
            raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name, send_Error
            )
        
        return True
    except FeatureDisabled:
        raise FeatureDisabled(
                f"Feature '{cog_name}' is disabled in this server.",
                cog_name, send_Error
            )
    except Exception:
        return True  # Allow feature by default on error


async def set_owner(bot: commands.Bot) -> Optional[User]:
    global owner
    if overwriteOwner:
        owner = await bot.fetch_user(overwriteOwner)  # Use fetch_user instead of get_user
        return owner
    try:
        app_info = await bot.application_info()
        if hasattr(app_info, 'team') and app_info.team:
            owner = await bot.fetch_user(app_info.team.owner_id)
        else:
            owner = app_info.owner
        
        return owner
    except Exception as e:
        print(f"Error in set_owner: {e}")
        return None

async def get_owner(bot: commands.Bot) -> Optional[User]:
    global owner
    
    # If owner is already set, return it
    if owner is not None:
        return owner
    # Otherwise, set and return the owner
    return await set_owner(bot)
class TypingManager:
    def __init__(self, client: Client):
        self.client = client
        self.active_typing: Dict[int, asyncio.Task] = {}
    
    async def start_typing(self, channel_id: int) -> None:
        """Start typing indicator in a channel."""
        channel = self.client.get_channel(channel_id)
        if not channel:
            channel = await self.client.fetch_channel(channel_id)
            if not channel:
                logger.warning(f"Invalid channel ID: {channel_id}")
                return

        try:
            async with channel.typing():
                while channel_id in self.active_typing:
                    await asyncio.sleep(5)  # Refresh typing indicator every 5 seconds
        except Exception as e:
            logger.error(f"Error in typing loop for channel {channel_id}: {str(e)}")
        finally:
            await self.stop_typing(channel_id)

    async def stop_typing(self, channel_id: int) -> None:
        """Stop typing indicator in a channel."""
        if channel_id in self.active_typing:
            task = self.active_typing.pop(channel_id)
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def trigger_typing(self, channel_id: int) -> None:
        """Trigger typing indicator for a channel."""
        # Stop any existing typing indicator
        await self.stop_typing(channel_id)
        
        # Create and store new typing task
        task = asyncio.create_task(self.start_typing(channel_id))
        self.active_typing[channel_id] = task

    async def cleanup(self) -> None:
        """Clean up all typing indicators."""
        for channel_id in list(self.active_typing.keys()):
            await self.stop_typing(channel_id)

class CommandDisabled(commands.CheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command is disabled.")

def enableByConfig(configOption: bool):
    async def predicate(ctx):
        if not configOption:
            raise CommandDisabled()
        return True
    return commands.check(predicate)
