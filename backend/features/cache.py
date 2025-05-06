from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict
from cachetools import TTLCache
import logging

from nexon.types.oauth2 import User


class CacheManager:
    """Manages caching for dashboard data"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        # Cache durations in seconds
        self.USER_CACHE_TTL = 3600  # 1 hour
        self.TOKEN_CACHE_TTL = 3600  # 1 hour
        self.GUILD_CACHE_TTL = 300  # 5 minutes

        # Initialize caches
        self.user_cache: TTLCache[str, User] = TTLCache(
            maxsize=10000, ttl=self.USER_CACHE_TTL
        )

    def cache_user(self, access_token: str, user_data: User) -> None:
        """Cache user data"""
        self.user_cache[access_token] = user_data

    def get_cached_user(self, access_token: str) -> Optional[User]:
        """Get cached user data"""
        return self.user_cache.get(access_token)
    
    async def __aenter__(self):
        # No async resources to initialize, just return self
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Properly clear all caches on exit
        self.user_cache.clear()