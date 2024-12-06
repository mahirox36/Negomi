import asyncio
import functools
import time
from typing import Any, Callable, List, Optional, Union, Coroutine

from modules.Nexon import logger
from .other import remove_numbers, url
from .config import BotConfig, overwriteOwner
from nextcord import AppInfo, ApplicationCheckFailure, Embed, Guild, Member, PermissionOverwrite, Interaction as init, Permissions, User
from nextcord.ext import commands
from nextcord.ext.application_checks import check
from nextcord.errors import ApplicationCheckFailure
from .Data import Data, DataGlobal
colour = BotConfig.General_Embeds_Colour

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
    embed =Embed(title=title,description=description,color=colour.Debug.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def info_embed(
    description: str = None,
    title: str = "Info",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colour.Info.value)
    if footer: embed.set_footer(text=footer)
    if author != None: embed.set_author(name=author[0],icon_url=author[1])
    return embed

def warn_embed(
    description: str = None,
    title: str = "Warn",
    footer: str = None,
    author: List[Union[str, url]] = None
) -> Embed:
    embed =Embed(title=title,description=description,color=colour.Warn.value)
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
    embed =Embed(title=title,description=description,color=colour.Error.value)
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
    
def userCTX(ctx:init):
    try:
        ctx.user = ctx.author
    except:
        pass
    return ctx
def userCONTEXT(ctx:init):
    try:
        ctx.author = ctx.user
    except:
        pass
    return ctx


async def high(ctx:init,user:Member):
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
    def __init__(self, message: Optional[str] = None,cog: Optional[str] = None) -> None:
        self.cog = cog
        super().__init__(message or "This command is disabled.")

def feature():
    def predicate(ctx: init) -> bool:
        file = DataGlobal("Feature", ctx.guild.id)
        applied_feature = file.data if file.data is not None else []
        name = remove_numbers(ctx.application_command.parent_cog.__class__.__name__)
        if name.lower() in applied_feature:
            raise FeatureDisabled(f"Feature '{name}' is disabled.",name)
        return True  # Check passed
    return check(predicate)
def featureInside(guildID: int, cog: object):
    cogName= cog.__class__.__name__.lower()
    file = DataGlobal("Feature", guildID)
    applied_feature = file.data if file.data is not None else []
    if cogName in applied_feature:
        raise FeatureDisabled(f"Feature '{cogName}' is disabled.",cogName)
    return True  # Check passed


async def set_owner(bot: commands.Bot):
    global owner
    if overwriteOwner:
        owner = bot.get_user(overwriteOwner)
        return owner
    try:
        app_info= await bot.application_info()
        if app_info.owner.name.startswith("team"):
            user = bot.get_user(app_info.team.owner.id)
        else:
            user = app_info.owner
        owner = user
        return owner
    except: pass
    
class TypingManager:
    def __init__(self, client):
        self.client = client
        self.active_typing = {}  # Store active typing tasks
        self.typing_locks = {}   # Prevent multiple typing indicators in same channel

    async def start_typing(self, channel_id: int):
        """Start typing indicator in a channel with proper cleanup."""
        if channel_id in self.active_typing:
            return  # Already typing in this channel

        channel = self.client.get_channel(channel_id)
        if not channel:
            return

        self.active_typing[channel_id] = True
        
        try:
            while self.active_typing.get(channel_id):
                async with channel.typing():
                    await asyncio.sleep(5)  # Discord typing indicator lasts ~10s, refresh every 5s
        except Exception as e:
            logger.error(f"Error in typing loop for channel {channel_id}: {e}")
        finally:
            self.stop_typing(channel_id)

    def stop_typing(self, channel_id: int):
        """Stop typing indicator in a channel."""
        self.active_typing.pop(channel_id, None)
        self.typing_locks.pop(channel_id, None)

    async def trigger_typing(self, channel_id: int):
        """Trigger typing indicator with proper locking and task management."""
        if channel_id in self.typing_locks:
            return

        self.typing_locks[channel_id] = True
        
        try:
            typing_task = asyncio.create_task(self.start_typing(channel_id))
            self.active_typing[channel_id] = typing_task
            return typing_task
        except Exception as e:
            logger.error(f"Error creating typing task for channel {channel_id}: {e}")
            self.stop_typing(channel_id)
