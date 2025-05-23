import asyncio
import hashlib
import json
import logging
import time
import weakref
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import (
    Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union,
    Awaitable, Tuple, NamedTuple
)
import pickle
import zlib
from concurrent.futures import ThreadPoolExecutor

from nexon.OAuth2.session import OAuth2Session
from nexon.OAuth2.token import OAuth2Token
from nexon.types.oauth2 import Guild, User
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.apiManager import APIServer
    

logger = logging.getLogger(__name__)

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Machine learning based
    HIERARCHICAL = "hierarchical"  # Multi-level caching


class CacheLevel(Enum):
    """Cache levels for hierarchical caching"""
    L1_MEMORY = 1  # Ultra-fast in-memory
    L2_COMPRESSED = 2  # Compressed in-memory
    L3_PERSISTENT = 3  # Disk-based cache


class Priority(Enum):
    """Cache priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class CacheMetrics:
    """Comprehensive cache metrics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    access_frequency: float = 0.0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        total = self.hits + self.misses
        self.hit_rate = self.hits / total if total > 0 else 0.0


@dataclass
class CacheEntry(Generic[T]):
    """Enhanced cache entry with comprehensive metadata"""
    key: str
    value: T
    created_at: float
    expires_at: Optional[float] = None
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    access_frequency: float = 0.0
    priority: Priority = Priority.MEDIUM
    tags: Set[str] = field(default_factory=set)
    size: int = 0
    compressed: bool = False
    checksum: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        self.size = self._calculate_size()
        self.checksum = self._calculate_checksum()
    
    def _calculate_size(self) -> int:
        """Calculate memory size of the cached value"""
        try:
            return len(pickle.dumps(self.value))
        except:
            return len(str(self.value))
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum for data integrity"""
        try:
            data = pickle.dumps(self.value)
            return hashlib.sha256(data).hexdigest()
        except:
            return hashlib.sha256(str(self.value).encode()).hexdigest()
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def touch(self):
        """Update access statistics"""
        current_time = time.time()
        self.access_count += 1
        time_since_creation = current_time - self.created_at
        self.access_frequency = self.access_count / max(time_since_creation, 1)
        self.last_accessed = current_time
    
    def verify_integrity(self) -> bool:
        """Verify data integrity using checksum"""
        return self.checksum == self._calculate_checksum()


class CacheInvalidationStrategy(ABC):
    """Abstract base for cache invalidation strategies"""
    
    @abstractmethod
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Determine if an entry should be invalidated"""
        pass


class TimeBasedInvalidation(CacheInvalidationStrategy):
    """Time-based cache invalidation"""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        return entry.is_expired()


class DependencyInvalidation(CacheInvalidationStrategy):
    """Dependency-based cache invalidation"""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        invalidated_keys = context.get('invalidated_keys', set())
        return bool(entry.dependencies.intersection(invalidated_keys))
    
    def add_dependency(self, dependent: str, dependency: str):
        """Add a dependency relationship"""
        self.dependency_graph[dependency].add(dependent)
    
    def get_dependents(self, key: str) -> Set[str]:
        """Get all keys that depend on the given key"""
        dependents = set()
        to_check = [key]
        
        while to_check:
            current = to_check.pop()
            for dependent in self.dependency_graph.get(current, set()):
                if dependent not in dependents:
                    dependents.add(dependent)
                    to_check.append(dependent)
        
        return dependents


class AdaptiveInvalidation(CacheInvalidationStrategy):
    """ML-based adaptive cache invalidation"""
    
    def __init__(self):
        self.access_patterns: Dict[str, List[float]] = defaultdict(list)
        self.prediction_threshold = 0.1
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        # Simple prediction based on access patterns
        key = entry.key
        current_time = time.time()
        
        # Record access pattern
        self.access_patterns[key].append(current_time)
        
        # Keep only recent history (last 100 accesses)
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
        
        # Predict if this entry will be accessed soon
        if len(self.access_patterns[key]) < 3:
            return False
        
        recent_accesses = self.access_patterns[key][-10:]
        avg_interval = sum(
            recent_accesses[i] - recent_accesses[i-1] 
            for i in range(1, len(recent_accesses))
        ) / max(len(recent_accesses) - 1, 1)
        
        time_since_last = current_time - entry.last_accessed
        predicted_next_access = entry.last_accessed + avg_interval
        
        # If we predict no access soon and it's been a while, invalidate
        return (time_since_last > avg_interval * 2 and 
                current_time > predicted_next_access + avg_interval)


class CacheBackend(ABC, Generic[K, V]):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: K) -> Optional[V]:
        pass
    
    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: K) -> bool:
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        pass
    
    @abstractmethod
    async def exists(self, key: K) -> bool:
        pass


class MemoryBackend(CacheBackend[str, CacheEntry]):
    """High-performance in-memory cache backend"""
    
    def __init__(self, max_size: int = 10000):
        self.data: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        async with self._lock:
            if key in self.data:
                entry = self.data[key]
                # Move to end (LRU)
                self.data.move_to_end(key)
                return entry
            return None
    
    async def set(self, key: str, value: CacheEntry, ttl: Optional[int] = None) -> None:
        async with self._lock:
            if len(self.data) >= self.max_size and key not in self.data:
                # Evict least recently used
                self.data.popitem(last=False)
            
            self.data[key] = value
            self.data.move_to_end(key)
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            return self.data.pop(key, None) is not None
    
    async def clear(self) -> None:
        async with self._lock:
            self.data.clear()
    
    async def exists(self, key: str) -> bool:
        return key in self.data


class CompressedBackend(CacheBackend[str, CacheEntry]):
    """Compressed memory backend for larger datasets"""
    
    def __init__(self, compression_level: int = 6):
        self.data: Dict[str, bytes] = {}
        self.compression_level = compression_level
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        async with self._lock:
            if key in self.data:
                compressed_data = self.data[key]
                pickled_data = zlib.decompress(compressed_data)
                return pickle.loads(pickled_data)
            return None
    
    async def set(self, key: str, value: CacheEntry, ttl: Optional[int] = None) -> None:
        async with self._lock:
            pickled_data = pickle.dumps(value)
            compressed_data = zlib.compress(pickled_data, self.compression_level)
            self.data[key] = compressed_data
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            return self.data.pop(key, None) is not None
    
    async def clear(self) -> None:
        async with self._lock:
            self.data.clear()
    
    async def exists(self, key: str) -> bool:
        return key in self.data


class HierarchicalCacheManager:
    """Multi-level hierarchical cache manager"""
    
    def __init__(self):
        self.levels: Dict[CacheLevel, CacheBackend] = {
            CacheLevel.L1_MEMORY: MemoryBackend(max_size=1000),
            CacheLevel.L2_COMPRESSED: CompressedBackend(),
        }
        self.metrics = CacheMetrics()
        self.invalidation_strategies: List[CacheInvalidationStrategy] = [
            TimeBasedInvalidation(),
            DependencyInvalidation(),
            AdaptiveInvalidation()
        ]
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats_lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with hierarchical lookup"""
        async with self._stats_lock:
            self.metrics.access_count += 1
        
        # Check each cache level
        for level in [CacheLevel.L1_MEMORY, CacheLevel.L2_COMPRESSED]:
            backend = self.levels.get(level)
            if backend:
                entry = await backend.get(key)
                if entry and not entry.is_expired():
                    entry.touch()
                    
                    # Promote to higher cache level if not already there
                    if level != CacheLevel.L1_MEMORY:
                        await self._promote_entry(key, entry, level)
                    
                    async with self._stats_lock:
                        self.metrics.hits += 1
                        self.metrics.update_hit_rate()
                    
                    return entry.value
        
        async with self._stats_lock:
            self.metrics.misses += 1
            self.metrics.update_hit_rate()
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        priority: Priority = Priority.MEDIUM,
        tags: Optional[Set[str]] = None,
        dependencies: Optional[Set[str]] = None
    ) -> None:
        """Set value in cache with intelligent placement"""
        current_time = time.time()
        expires_at = current_time + ttl if ttl else None
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            expires_at=expires_at,
            priority=priority,
            tags=tags or set(),
            dependencies=dependencies or set()
        )
        
        # Determine appropriate cache level based on size and priority
        cache_level = self._determine_cache_level(entry)
        backend = self.levels[cache_level]
        
        await backend.set(key, entry, ttl)
        
        # Add dependency tracking
        if dependencies:
            dep_strategy = next(
                (s for s in self.invalidation_strategies 
                 if isinstance(s, DependencyInvalidation)), None
            )
            if dep_strategy:
                for dep in dependencies:
                    dep_strategy.add_dependency(key, dep)
    
    async def delete(self, key: str) -> bool:
        """Delete from all cache levels"""
        deleted = False
        for backend in self.levels.values():
            if await backend.delete(key):
                deleted = True
        
        # Invalidate dependents
        await self._invalidate_dependents(key)
        
        return deleted
    
    async def invalidate_by_tags(self, tags: Set[str]) -> int:
        """Invalidate all entries matching any of the given tags"""
        invalidated = 0
        keys_to_delete = []
        
        for backend in self.levels.values():
            if hasattr(backend, 'data'):
                for key, entry_data in backend.data.items():
                    try:
                        if isinstance(backend, CompressedBackend):
                            # Decompress to check tags
                            pickled_data = zlib.decompress(entry_data)
                            entry = pickle.loads(pickled_data)
                        else:
                            entry = entry_data
                        
                        if entry.tags.intersection(tags):
                            keys_to_delete.append(key)
                    except Exception as e:
                        logger.warning(f"Error checking tags for key {key}: {e}")
        
        for key in keys_to_delete:
            if await self.delete(key):
                invalidated += 1
        
        return invalidated
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        async with self._stats_lock:
            stats = {
                'metrics': {
                    'hits': self.metrics.hits,
                    'misses': self.metrics.misses,
                    'hit_rate': self.metrics.hit_rate,
                    'access_count': self.metrics.access_count,
                    'evictions': self.metrics.evictions,
                },
                'memory_usage': {},
                'level_stats': {}
            }
        
        # Get per-level statistics
        for level, backend in self.levels.items():
            if hasattr(backend, 'data'):
                entry_count = len(backend.data)
                memory_usage = sum(
                    len(pickle.dumps(entry)) if not isinstance(backend, CompressedBackend)
                    else len(entry_data)
                    for entry_data in backend.data.values()
                )
                
                stats['level_stats'][level.name] = {
                    'entry_count': entry_count,
                    'memory_usage': memory_usage
                }
                stats['memory_usage'][level.name] = memory_usage
        
        return stats
    
    def _determine_cache_level(self, entry: CacheEntry) -> CacheLevel:
        """Determine optimal cache level for entry"""
        if entry.priority in [Priority.CRITICAL, Priority.HIGH]:
            return CacheLevel.L1_MEMORY
        elif entry.size > 10000:  # Large entries go to compressed cache
            return CacheLevel.L2_COMPRESSED
        else:
            return CacheLevel.L1_MEMORY
    
    async def _promote_entry(self, key: str, entry: CacheEntry, current_level: CacheLevel):
        """Promote entry to higher cache level"""
        if current_level == CacheLevel.L2_COMPRESSED:
            l1_backend = self.levels[CacheLevel.L1_MEMORY]
            await l1_backend.set(key, entry)
    
    async def _invalidate_dependents(self, key: str):
        """Invalidate all entries that depend on the given key"""
        dep_strategy = next(
            (s for s in self.invalidation_strategies 
             if isinstance(s, DependencyInvalidation)), None
        )
        
        if dep_strategy:
            dependents = dep_strategy.get_dependents(key)
            for dependent in dependents:
                await self.delete(dependent)
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    async def stop_background_tasks(self):
        """Stop background maintenance tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_expired(self):
        """Background task to clean up expired entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                keys_to_delete = []
                context = {'invalidated_keys': set()}
                
                for backend in self.levels.values():
                    if hasattr(backend, 'data'):
                        for key, entry_data in list(backend.data.items()):
                            try:
                                if isinstance(backend, CompressedBackend):
                                    pickled_data = zlib.decompress(entry_data)
                                    entry = pickle.loads(pickled_data)
                                else:
                                    entry = entry_data
                                
                                # Check all invalidation strategies
                                should_invalidate = False
                                for strategy in self.invalidation_strategies:
                                    if await strategy.should_invalidate(entry, context):
                                        should_invalidate = True
                                        break
                                
                                if should_invalidate:
                                    keys_to_delete.append(key)
                                    context['invalidated_keys'].add(key)
                            
                            except Exception as e:
                                logger.warning(f"Error during cleanup for key {key}: {e}")
                                keys_to_delete.append(key)  # Remove corrupted entries
                
                # Delete expired/invalid entries
                for key in keys_to_delete:
                    await self.delete(key)
                    async with self._stats_lock:
                        self.metrics.evictions += 1
                
                if keys_to_delete:
                    logger.info(f"Cleaned up {len(keys_to_delete)} cache entries")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}")


def cache_key_generator(*args, **kwargs) -> str:
    """Generate a consistent cache key from function arguments"""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if hasattr(arg, '__dict__'):
            # For objects, use class name and relevant attributes
            key_parts.append(f"{arg.__class__.__name__}:{hash(str(arg))}")
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()


def cached(
    ttl: Optional[int] = 3600,
    priority: Priority = Priority.MEDIUM,
    tags: Optional[Set[str]] = None,
    dependencies: Optional[Set[str]] = None,
    key_generator: Optional[Callable] = None
):
    """Advanced caching decorator with comprehensive features"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                func_name = f"{func.__module__}.{func.__qualname__}"
                cache_key = f"{func_name}:{cache_key_generator(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(
                cache_key, result, ttl=ttl, priority=priority,
                tags=tags, dependencies=dependencies
            )
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle caching differently
            # This is a simplified version - in practice, you might want
            # to use a separate sync cache manager
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Global cache manager instance
cache_manager = HierarchicalCacheManager()


# Enhanced versions of your original functions
@cached(ttl=3600, priority=Priority.HIGH, tags={"discord", "guilds"})
async def get_cached_guilds(backend: "APIServer", access_token: str) -> List[Guild]:
    """Enhanced guild caching with intelligent invalidation"""
    oauth_token = OAuth2Token({
        "access_token": access_token,
        "token_type": "Bearer",
    })
    session = OAuth2Session(backend.oauth_client, oauth_token)
    guilds = await session.fetch_guilds()
    return guilds


@cached(ttl=1800, priority=Priority.HIGH, tags={"discord", "user"})
async def get_cached_user(backend: "APIServer", access_token: str) -> User:
    """Enhanced user caching with dependency tracking"""
    oauth_token = OAuth2Token({
        "access_token": access_token,
        "token_type": "Bearer",
    })
    session = OAuth2Session(backend.oauth_client, oauth_token)
    user = await session.fetch_user()
    return user


@cached(ttl=7200, priority=Priority.MEDIUM, tags={"dashboard", "user_stats"})
async def get_cached_user_dashboard(
    backend: "APIServer", 
    access_token: str, 
    user_id: int
) -> Dict:
    """Cache comprehensive dashboard data with smart invalidation"""
    # This would contain your dashboard logic
    # Dependencies would include user data, guild data, etc.
    pass


# Context manager for cache transactions
@asynccontextmanager
async def cache_transaction():
    """Context manager for cache transactions with rollback capability"""
    transaction_keys = []
    try:
        yield transaction_keys
    except Exception:
        # Rollback - remove all keys added during transaction
        for key in transaction_keys:
            await cache_manager.delete(key)
        raise


# Cache warming utility
async def warm_cache(patterns: List[Tuple[Callable, List, Dict]]):
    """Pre-warm cache with common queries"""
    tasks = []
    for func, args, kwargs in patterns:
        task = asyncio.create_task(func(*args, **kwargs))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for r in results if not isinstance(r, Exception))
    logger.info(f"Cache warming completed: {successful}/{len(patterns)} successful")


# Integration with APIServer class
class CacheIntegration:
    """Integration wrapper for APIServer compatibility"""
    
    def __init__(self, cache_manager: HierarchicalCacheManager):
        self.cache_manager = cache_manager
    
    async def get_cached_user(self, access_token: str) -> Optional[Dict]:
        """Get cached user - compatible with existing APIServer method"""
        return await self.cache_manager.get(f"user_{access_token}")
    
    def cache_user(self, access_token: str, user_data: Dict):
        """Cache user data - compatible with existing APIServer method"""
        asyncio.create_task(self.cache_manager.set(
            f"user_{access_token}", 
            user_data, 
            ttl=1800,  # 30 minutes
            priority=Priority.HIGH,
            tags={"discord", "user"}
        ))

# Create cache integration instance
cache_integration = CacheIntegration(cache_manager)

# Export the enhanced cache system
__all__ = [
    'cache_manager',
    'cache_integration',
    'cached',
    'get_cached_guilds',
    'get_cached_user',
    'get_cached_user_dashboard',
    'cache_transaction',
    'warm_cache',
    'Priority',
    'CacheStrategy',
    'HierarchicalCacheManager'
]