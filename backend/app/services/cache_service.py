"""
Caching service for dashboard statistics and frequently accessed data.

This module provides a simple in-memory caching layer with time-based
expiration for dashboard statistics. In production, this should be
replaced with Redis or Memcached for distributed caching.

Cache Strategy:
- Cache key: user_id
- Cache TTL: 5 seconds (configurable)
- Cache invalidation: Time-based expiration
- Thread-safe: Uses threading.Lock for concurrent access
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from threading import Lock
from dataclasses import dataclass

from app.schemas.dashboard import TaskStatistics


@dataclass
class CacheEntry:
    """
    Cache entry with data and expiration timestamp.

    Attributes:
        data: Cached data (any type)
        expires_at: Expiration timestamp (UTC)
        created_at: Creation timestamp (UTC)
    """
    data: Any
    expires_at: datetime
    created_at: datetime

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() >= self.expires_at


class CacheService:
    """
    Simple in-memory cache service with time-based expiration.

    This service provides a thread-safe in-memory cache for dashboard
    statistics and other frequently accessed data. Cache entries expire
    after a configurable TTL (default: 5 seconds).

    Note:
        This is a simple in-memory cache suitable for single-instance
        deployments. For production with multiple instances, use Redis
        or Memcached for distributed caching.

    Example:
        ```python
        cache = CacheService(ttl_seconds=5)

        # Set cache entry
        cache.set("user-123", statistics)

        # Get cache entry
        cached_stats = cache.get("user-123")
        if cached_stats:
            print("Cache hit!")
        else:
            print("Cache miss!")

        # Clear cache
        cache.clear()
        ```
    """

    def __init__(self, ttl_seconds: int = 5):
        """
        Initialize cache service.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 5)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data by key.

        This method retrieves cached data if it exists and hasn't expired.
        Expired entries are automatically removed.

        Args:
            key: Cache key (typically user_id)

        Returns:
            Cached data if found and not expired, None otherwise

        Example:
            ```python
            stats = cache.get("user-123")
            if stats:
                print(f"Cache hit: {stats}")
            else:
                print("Cache miss")
            ```
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            # Check if entry has expired
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                return None

            return entry.data

    def set(self, key: str, data: Any) -> None:
        """
        Set cached data with expiration.

        This method stores data in the cache with a TTL-based expiration.
        If an entry with the same key already exists, it will be replaced.

        Args:
            key: Cache key (typically user_id)
            data: Data to cache (any type)

        Example:
            ```python
            cache.set("user-123", statistics)
            ```
        """
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=self._ttl_seconds)
            entry = CacheEntry(
                data=data,
                expires_at=expires_at,
                created_at=datetime.utcnow()
            )
            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """
        Delete cached data by key.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise

        Example:
            ```python
            deleted = cache.delete("user-123")
            if deleted:
                print("Cache entry deleted")
            ```
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """
        Clear all cached data.

        This method removes all entries from the cache.

        Example:
            ```python
            cache.clear()
            print("Cache cleared")
            ```
        """
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        This method scans the cache and removes all expired entries.
        It should be called periodically to prevent memory leaks.

        Returns:
            Number of expired entries removed

        Example:
            ```python
            removed = cache.cleanup_expired()
            print(f"Removed {removed} expired entries")
            ```
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            dict: Cache statistics including size, hit rate, etc.

        Example:
            ```python
            stats = cache.get_stats()
            print(f"Cache size: {stats['size']}")
            ```
        """
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values()
                if entry.is_expired()
            )

            return {
                "size": total_entries,
                "expired": expired_entries,
                "active": total_entries - expired_entries,
                "ttl_seconds": self._ttl_seconds
            }


# Global cache instance (singleton pattern)
# In production, this should be replaced with Redis or Memcached
_cache_instance: Optional[CacheService] = None


def get_cache_service(ttl_seconds: int = 5) -> CacheService:
    """
    Get or create global cache service instance.

    This function implements the singleton pattern to ensure only one
    cache instance exists throughout the application lifecycle.

    Args:
        ttl_seconds: Time-to-live for cache entries (default: 5)

    Returns:
        CacheService: Global cache service instance

    Example:
        ```python
        cache = get_cache_service()
        cache.set("user-123", data)
        ```
    """
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = CacheService(ttl_seconds=ttl_seconds)

    return _cache_instance


def invalidate_user_cache(user_id: str) -> bool:
    """
    Invalidate cache for a specific user.

    This function should be called when user data changes (e.g., task
    created, updated, or deleted) to ensure cache consistency.

    Args:
        user_id: User identifier

    Returns:
        bool: True if cache was invalidated, False if no cache entry existed

    Example:
        ```python
        # After creating a task
        task = create_task(user_id, title, description)
        invalidate_user_cache(user_id)
        ```
    """
    cache = get_cache_service()
    return cache.delete(user_id)


def clear_all_cache() -> None:
    """
    Clear all cached data.

    This function should be used sparingly, typically only during
    testing or maintenance operations.

    Example:
        ```python
        clear_all_cache()
        print("All cache cleared")
        ```
    """
    cache = get_cache_service()
    cache.clear()


# Cache decorator for functions
def cached(ttl_seconds: int = 5):
    """
    Decorator to cache function results.

    This decorator caches the result of a function based on its arguments.
    The cache key is generated from the function name and arguments.

    Args:
        ttl_seconds: Time-to-live for cache entries (default: 5)

    Returns:
        Decorated function with caching

    Example:
        ```python
        @cached(ttl_seconds=10)
        def expensive_computation(user_id: str) -> dict:
            # Expensive computation here
            return result
        ```

    Note:
        This is a simple implementation. For production, consider using
        functools.lru_cache or a more sophisticated caching library.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cache = get_cache_service(ttl_seconds=ttl_seconds)
            cached_result = cache.get(cache_key)

            if cached_result is not None:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result)

            return result

        return wrapper
    return decorator
