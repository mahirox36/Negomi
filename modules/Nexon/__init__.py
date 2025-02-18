"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""
#This Library Custom Classes and functions
import nest_asyncio
nest_asyncio.apply()


from .DataManager import DataManager
from .BetterID import BetterID
from .config import BotConfig
from .config import *
from .sidecord import PermissionOverwriteWith, PermissionsWith, owner, get_name, everyone, debug_embed, info_embed, warn_embed, \
    error_embed, SlashCommandOnCooldown,HaveHigherRole, ApplicationNotOwnerGuild, cooldown, is_owner_guild, \
    FeatureDisabled, remove_numbers, get_feature_state, feature, check_feature_inside, set_owner, get_owner, TypingManager, \
        CommandDisabled, enableByConfig, url, extract_emojis, contains_emoji, get_by_percent
from .logger import logger, print
from .Negomi import ConversationManager, generate, download_model, client as negomi, offline, online, isClientOnline
from .Users import UserManager as UserData
from .ipc_manager import IPCManager

#Important things
from typing import Any, Callable, Dict, List, Set, Optional, Union
import os
from pathlib import Path
import json
import asyncio
import io
from datetime import datetime
# Every class/functions I used in nextcord
from nexon import (
    Client, Interaction as init, Member, Interaction,
    Permissions, Role, slash_command, Activity, Attachment,
    Button, ButtonStyle, CategoryChannel, ChannelType, DMChannel, Embed, Emoji,
    File, Guild, Message, TextChannel, VoiceChannel, ForumChannel, GroupChannel, StageChannel, Colour,
    ui, SelectOption, Interaction, SlashOption, user_command, VoiceState, message_command,
    User, PermissionOverwrite, __version__ as nextcord_version, InteractionType, InteractionContextType, FFmpegPCMAudio, VoiceClient,
    IntegrationType, Reaction, Thread, WebhookMessage, PartialInteractionMessage, InteractionMessage, ForumTag, SortOrderType, ForumLayoutType, VoiceRegion, VideoQualityMode
)
from nexon.ext import tasks
#Type Errors
from nexon import (
    HTTPException, Forbidden
)
# Other Stuff Like UI, application_checks, commands
from nexon.ui import View, Button, TextInput, Modal, ChannelSelect, RoleSelect, Item, MentionableSelect, UserSelect, StringSelect, button
from nexon.ext.application_checks import *
from nexon.ext import commands
from nexon.ext.commands import Bot
from nexon import utils
import sys

