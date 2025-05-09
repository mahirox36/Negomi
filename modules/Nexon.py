"""
Core Library with Functions, Classes, Bot Config, Embeds, AI System, and Nextcord Shortcuts
~~~~~~~~~~~~~~~
"""
#This Library Custom Classes and functions
import nest_asyncio
nest_asyncio.apply()


from nexon import MemberData, UserData, Feature, ScopeType, utils
from .DiscordConfig import *
from .utils import extract_emojis, get_by_percent, remove_numbers, emoji, IDManager
from rich.console import Console
import logging
console = Console(force_terminal=True)

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

logger = logging.getLogger(__name__)

from .Negomi import ConversationManager, generate, download_model, client as negomi, offline, online, isClientOnline

#Important things
from typing import Any, Callable, Dict, List, Set, Optional, Union
import os
from pathlib import Path
import json
import asyncio
import io
from datetime import datetime, timezone
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
MISSING: Any = utils.MISSING

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
        response = r2quest.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Open the image
        image = Image.open(BytesIO(response.content))

        img_byte_arr = BytesIO()

        # Set max size and quality parameters
        max_size = 128
        max_file_size = 256 * 1024  # 256 KB
        quality_level = 90

        if image.format == "GIF":
            # Reduce GIF frame count and size
            frames = []
            for i, frame in enumerate(ImageSequence.Iterator(image)):
                if i >= 20:  # Limit to maximum 20 frames
                    break
                # Skip frames to reduce file size if there are too many
                if i > 10 and i % 2 != 0:
                    continue
                
                # Resize the frame and convert to adaptive palette
                resized_frame = frame.copy()
                if max(resized_frame.width, resized_frame.height) > max_size:
                    ratio = max_size / max(resized_frame.width, resized_frame.height)
                    new_size = (int(resized_frame.width * ratio), int(resized_frame.height * ratio))
                    resized_frame = resized_frame.resize(new_size, Image.Resampling.LANCZOS)
                
                frames.append(resized_frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))

            # Save optimized GIF
            if frames:
                frames[0].save(
                    img_byte_arr,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    loop=image.info.get("loop", 0),
                    duration=image.info.get("duration", 100),
                    optimize=True
                )
            else:
                # Fallback if no frames were processed
                return None

        else:
            # Resize for static images
            if max(image.width, image.height) > max_size:
                ratio = max_size / max(image.width, image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Try PNG first
            image.save(img_byte_arr, format="PNG", optimize=True)

            # If PNG is too large, try JPEG with adjustable quality
            if img_byte_arr.tell() > max_file_size:
                img_byte_arr = BytesIO()  # Reset buffer
                
                # Convert to RGB (removing alpha channel if present)
                rgb_image = image.convert("RGB")
                
                # Try different quality levels until we get under the size limit
                while quality_level > 50:
                    img_byte_arr = BytesIO()  # Reset buffer
                    rgb_image.save(img_byte_arr, format="JPEG", quality=quality_level, optimize=True)
                    if img_byte_arr.tell() <= max_file_size:
                        break
                    quality_level -= 10

        # Final size check
        file_size = img_byte_arr.tell()
        if file_size > max_file_size:
            logger.warning(f"Image still too large after compression: {file_size} bytes")
            # Last resort: if still too large, return a heavily reduced version
            if file_size > max_file_size * 1.5:
                img_byte_arr = BytesIO()
                very_small = image.resize((64, 64), Image.Resampling.LANCZOS).convert("RGB")
                very_small.save(img_byte_arr, format="JPEG", quality=60)

        # Return the bytes
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    except r2quest.RequestException as e:
        logger.error(f"Failed to download image from {url}: {e}")
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
    
    return None