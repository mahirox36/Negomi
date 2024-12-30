"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""
#This Library Custom Classes and functions
from .Data import Data, DataGlobal
from .BetterID import BetterID
from .config import BotConfig
from .config import *
from .sidecord import PermissionOverwriteWith, PermissionsWith, owner, get_name, everyone, debug_embed, info_embed, warn_embed, \
    error_embed, SlashCommandOnCooldown,HaveHigherRole, ApplicationNotOwnerGuild, cooldown, is_owner_guild, \
    FeatureDisabled, remove_numbers, get_feature_state, feature, check_feature_inside, set_owner, get_owner, TypingManager, \
        CommandDisabled, enableByConfig
from .other import url, clear, remove_prefix, word_to_number, time_units, text_to_number, convert_to_seconds, \
    remove_numbers, get_resource_path, is_executable
from .logger import logger, print
from .Negomi import ConversationManager, generate, download_model

#Important things
from typing import Any, Callable, Dict, List, Set, Optional, Union
import os
from pathlib import Path
import json
import asyncio
import io
from datetime import datetime
# Every class/functions I used in nextcord
from nextcord import (
    Client, Interaction as init, Member,
    Permissions, Role, slash_command, Activity, Attachment,
    Button, ButtonStyle, CategoryChannel, ChannelType, DMChannel, Embed, Emoji,
    File, Guild, Message, TextChannel, VoiceChannel, ForumChannel, GroupChannel, StageChannel, Colour,
    ui, SelectOption, Interaction, SlashOption, user_command, VoiceState,
    User, PermissionOverwrite, __version__ as nextcord_version
)
#Type Errors
from nextcord import (
    HTTPException, Forbidden
)
# Other Stuff Like UI, application_checks, commands
from nextcord.ui import View, Button, TextInput, Modal, ChannelSelect, RoleSelect, Item, MentionableSelect, UserSelect, StringSelect
from nextcord.ext.application_checks import *
from nextcord.ext import commands