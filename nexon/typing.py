# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Union

from .channel import (
    TextChannel, 
    VoiceChannel,
    GroupChannel,
    StageChannel,
    Thread,
    DMChannel,
)

__all__ = (
    "TypingManager",
)


class TypingManager:
    """Manages typing indicators for channels."""

    def __init__(self) -> None:
        """Initializes the typing manager.

        Args:
            client: The client instance.
        """
        self.active_typing: Dict[int, asyncio.Task] = {}

    async def start_typing(self, channel: Union[TextChannel, VoiceChannel, GroupChannel, StageChannel, Thread, DMChannel], max_time: int = 120, refresh_time: int = 5) -> None:
        """Starts typing indicator in a channel.

        Args:
            channel: The ID of the channel.

        Raises:
            Exception: If an error occurs while starting the typing indicator.
        """
        try:
            async with channel.typing():
                while channel.id in self.active_typing or max_time <= 0:
                    max_time -= refresh_time
                    await asyncio.sleep(refresh_time)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error in typing loop for channel {channel.id}: {str(e)}")
        finally:
            await self.stop_typing(channel.id)

    async def stop_typing(self, channel_id: int) -> None:
        """Stops typing indicator in a channel.

        Args:
            channel: The ID of the channel.
        """
        if channel_id in self.active_typing:
            task = self.active_typing.pop(channel_id)
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def trigger_typing(self, channel: Union[TextChannel, VoiceChannel, GroupChannel, StageChannel, Thread, DMChannel], time: int = 120) -> None:
        """Triggers typing indicator for a channel.

        Args:
            channel: The ID of the channel.
        """
        # Stop any existing typing indicator
        await self.stop_typing(channel.id)
        
        # Create and store new typing task
        task = asyncio.create_task(self.start_typing(channel, time))
        self.active_typing[channel.id] = task

    async def cleanup(self) -> None:
        """Cleans up all typing indicators."""
        for channel_id in list(self.active_typing.keys()):
            await self.stop_typing(channel_id)