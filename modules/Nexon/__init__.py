"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""

from .Data import Data, DataGlobal
from .BetterID import BetterID
from .config import BotConfig
from .config import *
from .sidecord import PermissionOverwriteWith, PermissionsWith, owner, get_name, everyone, debug_embed, info_embed, warn_embed, \
    error_embed, SlashCommandOnCooldown, userCTX, userCONTEXT, high, ApplicationNotOwnerGuild, cooldown, is_owner_guild, \
    FeatureDisabled, remove_numbers, get_feature_state, feature, check_feature_inside, set_owner, get_owner, TypingManager, \
        CommandDisabled, enableByConfig
from .other import url, clear, remove_prefix, word_to_number, time_units, text_to_number, convert_to_seconds, \
    remove_numbers, get_resource_path, is_executable
from .logger import logger, print
from .Negomi import ConversationManager, generate
from typing import Any, Callable, Dict, List, Optional, Union
import os
import json
from datetime import datetime
import asyncio