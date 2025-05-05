import io
import gc
import logging
import asyncio
from typing import Dict, Optional
from PIL import Image

logger = logging.getLogger("welcome.cache")


class WelcomeCacheManager:
    """Manages caching for welcome images, avatars, fonts, and other resources"""

    def __init__(self):
        """Initialize caches and cleanup mechanisms"""
        self.font_cache: Dict[str, object] = {}
        self.avatar_cache: Dict[str, Image.Image] = {}
        self.image_cache: Dict[str, io.BytesIO] = {}
        self.background_cache: Dict[str, Image.Image] = {}
        self._cache_version = 0
        self._cache_max_size = 100
        self._cleanup_task = None
        self._setup_cleanup_task()

    def _setup_cleanup_task(self):
        """Setup regular cache cleanup task"""

        async def cleanup_loop():
            while True:
                await asyncio.sleep(3600)  # Cleanup once per hour
                self.cleanup_caches()

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    def cleanup_caches(self):
        """Clean up caches to prevent memory issues"""
        # Keep only the most recently used items if cache exceeds max size
        if len(self.avatar_cache) > self._cache_max_size:
            items = list(self.avatar_cache.items())
            self.avatar_cache = dict(items[-self._cache_max_size :])

        if len(self.background_cache) > self._cache_max_size:
            items = list(self.background_cache.items())
            self.background_cache = dict(items[-self._cache_max_size :])

        if len(self.image_cache) > self._cache_max_size:
            items = list(self.image_cache.items())
            self.image_cache = dict(items[-self._cache_max_size :])

        gc.collect()
        logger.debug(
            f"Cache cleaned up. Avatar: {len(self.avatar_cache)}, Background: {len(self.background_cache)}, Image: {len(self.image_cache)}"
        )

    def cleanup_if_needed(self):
        """Check if cache needs immediate cleanup"""
        total_items = (
            len(self.avatar_cache) + len(self.background_cache) + len(self.image_cache)
        )
        if total_items > self._cache_max_size * 2:
            self.cleanup_caches()

    def invalidate_caches(self, guild_id: Optional[int] = None):
        """Invalidate all relevant caches for a guild"""
        if guild_id:
            # Clear image cache entries for this guild
            self.image_cache = {
                k: v
                for k, v in self.image_cache.items()
                if not k.startswith(f"{guild_id}_")
            }
        else:
            self.image_cache.clear()
        self._cache_version += 1
        logger.debug(
            f"Caches invalidated for guild: {guild_id}. New version: {self._cache_version}"
        )

    def get_cache_version(self) -> int:
        """Get current cache version"""
        return self._cache_version

    def cache_avatar(self, url: str, image: Image.Image):
        """Cache an avatar image"""
        self.avatar_cache[url] = image

    def get_cached_avatar(self, url: str) -> Optional[Image.Image]:
        """Get a cached avatar image"""
        if url in self.avatar_cache:
            return self.avatar_cache[url].copy()
        return None

    def cache_background(self, url: str, image: Image.Image):
        """Cache a background image"""
        self.background_cache[url] = image

    def get_cached_background(self, url: str) -> Optional[Image.Image]:
        """Get a cached background image"""
        if url in self.background_cache:
            return self.background_cache[url].copy()
        return None

    def cache_image(self, key: str, image: io.BytesIO):
        """Cache a generated welcome image"""
        # Store a copy to avoid concurrent access issues
        image.seek(0)
        self.image_cache[key] = io.BytesIO(image.getvalue())

    def get_cached_image(self, key: str) -> Optional[io.BytesIO]:
        """Get a cached welcome image"""
        if key in self.image_cache:
            # Verify cached image is still valid
            try:
                cached = self.image_cache[key]
                cached.seek(0)
                # Return a copy so original stays in cache
                image_copy = io.BytesIO(cached.getvalue())
                cached.seek(0)
                return image_copy
            except (ValueError, OSError):
                # Remove invalid cached item
                del self.image_cache[key]
                return None
        return None

    def cache_font(self, key: str, font):
        """Cache a font object"""
        self.font_cache[key] = font

    def get_cached_font(self, key: str):
        """Get a cached font object"""
        return self.font_cache.get(key)

    def cleanup(self):
        """Cleanup all resources"""
        # Close all PIL images
        for img in self.avatar_cache.values():
            try:
                img.close()
            except:
                pass

        for img in self.background_cache.values():
            try:
                img.close()
            except:
                pass

        # Close all BytesIO objects
        for buf in self.image_cache.values():
            try:
                buf.close()
            except:
                pass

        # Clear dictionaries to help garbage collection
        self.avatar_cache.clear()
        self.background_cache.clear()
        self.image_cache.clear()
        self.font_cache.clear()

        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.cancelled():
            self._cleanup_task.cancel()

        gc.collect()
