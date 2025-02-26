"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""
#This Library Custom Classes and functions
import nest_asyncio
nest_asyncio.apply()


from nexon import DataManager, UserManager as UserData
from .DiscordConfig import *
from .utils import extract_emojis, get_by_percent, remove_numbers, emoji, IDManager
from .settings import FeatureManager, FeatureDisabled


import logging

Level = logger_level.lower()
if Level.startswith("n"): Level = logging.NOTSET
elif Level.startswith("d"): Level = logging.DEBUG
elif Level.startswith("i"): Level = logging.INFO
elif Level.startswith("w"): Level = logging.WARNING
elif Level.startswith("e"): Level = logging.ERROR
elif Level.startswith("c"): Level = logging.CRITICAL
else: Level = logging.INFO
logger = logging.getLogger("bot")

from .Negomi import ConversationManager, generate, download_model, client as negomi, offline, online, isClientOnline

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
from nexon.ext.application_checks import * # type: ignore
from nexon.ext import commands
from nexon.ext.commands import Bot
from nexon import utils
import sys

