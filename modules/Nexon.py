"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""
#This Library Custom Classes and functions
import nest_asyncio
nest_asyncio.apply()


from nexon import MemberData, UserData, Feature, ScopeType
from .DiscordConfig import *
from .utils import extract_emojis, get_by_percent, remove_numbers, emoji, IDManager


import logging

Level = logger_level.lower()
match Level[0]:
    case "n":
        Level = logging.NOTSET
    case "d":
        Level = logging.DEBUG
    case "i":
        Level = logging.INFO
    case "w":
        Level = logging.WARNING
    case "e":
        Level = logging.ERROR
    case "c":
        Level = logging.CRITICAL
    case _:
        Level = logging.INFO

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
    User, PermissionOverwrite, __version__ as nexon_version, InteractionType, InteractionContextType, FFmpegPCMAudio, VoiceClient,
    IntegrationType, Reaction, Thread, WebhookMessage, PartialInteractionMessage, InteractionMessage, ForumTag, SortOrderType,
    ForumLayoutType, VoiceRegion, VideoQualityMode, PartialMessageable
)
from nexon.ext import tasks
#Type Errors
from nexon import (
    HTTPException, Forbidden, ApplicationInvokeError
)
# Other Stuff Like UI, application_checks, commands
from nexon.ui import View, Button, TextInput, Modal, ChannelSelect, RoleSelect, Item, MentionableSelect, UserSelect, StringSelect, button
from nexon.ext.application_checks import * # type: ignore
from nexon.ext import commands
from nexon.ext.commands import Bot
from nexon import utils
import sys
import requests as r2quest
from io import BytesIO
from typing import Optional
from PIL import Image, ImageSequence

def download_image_to_bytes(url: str) -> Optional[bytes]:
    """
    Downloads an image (GIF or other formats) from the given URL, resizes it to 128x128,
    compresses it below 256 KB, and returns it as bytes.
    
    Args:
        url (str): The URL of the image to download.
    
    Returns:
        Optional[bytes]: The resized and compressed image data in bytes, or None if the process fails.
    """
    try:
        response = r2quest.get(url, stream=True)
        response.raise_for_status()

        # Open the image
        image = Image.open(BytesIO(response.content))

        img_byte_arr = BytesIO()

        if image.format == "GIF":
            # Reduce GIF frame count (if more than 10 frames, keep every 2nd frame)
            frames = [frame.copy().convert("P", palette=Image.Palette.ADAPTIVE, colors=128).resize((128, 128), Image.Resampling.LANCZOS)
                      for i, frame in enumerate(ImageSequence.Iterator(image)) if i % 2 == 0]

            # Save optimized GIF
            frames[0].save(
                img_byte_arr,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                loop=image.info.get("loop", 0),
                duration=image.info.get("duration", 50),
                optimize=True
            )

        else:
            # Resize for static images
            image = image.resize((128, 128), Image.Resampling.LANCZOS)

            # Try PNG first
            image.save(img_byte_arr, format="PNG", optimize=True)

            # If PNG is too large, try JPEG with adjustable quality
            if img_byte_arr.tell() > 256 * 1024:
                img_byte_arr = BytesIO()  # Reset buffer
                image.convert("RGB").save(img_byte_arr, format="JPEG", quality=85, optimize=True)

        # Check size limit
        if img_byte_arr.tell() > 256 * 1024:  # 256 KB
            logger.error(f"Image size ({img_byte_arr.tell()} bytes) exceeds Discord's 256 KB limit.")
            return None

        return img_byte_arr.getvalue()

    except r2quest.RequestException as e:
        logger.error(f"Failed to download image from {url}: {e}")
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
    
    return None