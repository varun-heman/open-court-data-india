"""
Caching utilities for court scrapers.

This module provides caching functionality for court scrapers to avoid
re-downloading content that hasn't changed.
"""
import os
import hashlib
import json
import time
from typing import Dict, Any, Optional, Union, Callable, TypeVar, cast
from datetime import datetime, timedelta
import logging

try:
    from diskcache import Cache
except ImportError:
    # Fallback to a simple file-based cache if diskcache is not available
    Cache = None


logger = logging.getLogger(__name__)

# Type variable for generic return type
T = TypeVar('T')


class ScraperCache:
    """
    Cache for court scrapers.
    
    This class provides caching functionality for court scrapers to avoid
    re-downloading content that hasn't changed.
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        expiration: int = 86400,  # 24 hours in seconds
        size_limit: int = 1024 * 1024 * 1024,  # 1GB
        shards: int = 8,
        disable_cache: bool = False
    ):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            expiration: Cache expiration time in seconds
            size_limit: Maximum cache size in bytes
            shards: Number of shards for diskcache
            disable_cache: Whether to disable caching
        """
        self.disable_cache = disable_cache
        
        if self.disable_cache:
            self.cache = None
            return
        
        # Default cache directory
        if not cache_dir:
            cache_dir = os.path.join(os.getcwd(), ".cache")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize cache
        if Cache:
            try:
                self.cache = Cache(
                    directory=cache_dir,
                    size_limit=size_limit,
                    shards=shards
                )
                self.cache.stats(enable=True)
                logger.info(f"Using diskcache at {cache_dir}")
            except Exception as e:
                logger.error(f"Error initializing diskcache: {e}")
                self.cache = None
                self.disable_cache = True
        else:
            logger.warning("diskcache not available, using simple file-based cache")
            self.cache = None
            self.cache_dir = cache_dir
        
        self.expiration = expiration
    
    def _get_key_hash(self, key: str) -> str:
        """
        Get hash for a cache key.
        
        Args:
            key: Cache key
        
        Returns:
            Hash of the key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get path to a cache file.
        
        Args:
            key: Cache key
        
        Returns:
            Path to cache file
        """
        key_hash = self._get_key_hash(key)
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
        
        Returns:
            Cached value or default
        """
        if self.disable_cache:
            return default
        
        if self.cache:
            # Using diskcache
            try:
                value = self.cache.get(key, default)
                if value is not None:
                    logger.debug(f"Cache hit for {key}")
                else:
                    logger.debug(f"Cache miss for {key}")
                return value
            except Exception as e:
                logger.error(f"Error getting from cache: {e}")
                return default
        else:
            # Using simple file-based cache
            try:
                cache_path = self._get_cache_path(key)
                if not os.path.exists(cache_path):
                    logger.debug(f"Cache miss for {key}")
                    return default
                
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                # Check if cache is expired
                if data['expiration'] < time.time():
                    logger.debug(f"Cache expired for {key}")
                    os.remove(cache_path)
                    return default
                
                logger.debug(f"Cache hit for {key}")
                return cast(T, data['value'])
            except Exception as e:
                logger.error(f"Error getting from cache: {e}")
                return default
    
    def set(self, key: str, value: Any, expiration: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expiration: Custom expiration time in seconds
        
        Returns:
            True if successful, False otherwise
        """
        if self.disable_cache:
            return False
        
        if expiration is None:
            expiration = self.expiration
        
        if self.cache:
            # Using diskcache
            try:
                self.cache.set(key, value, expire=expiration)
                logger.debug(f"Cached {key}")
                return True
            except Exception as e:
                logger.error(f"Error setting cache: {e}")
                return False
        else:
            # Using simple file-based cache
            try:
                cache_path = self._get_cache_path(key)
                
                data = {
                    'value': value,
                    'expiration': time.time() + expiration
                }
                
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
                
                logger.debug(f"Cached {key}")
                return True
            except Exception as e:
                logger.error(f"Error setting cache: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if successful, False otherwise
        """
        if self.disable_cache:
            return False
        
        if self.cache:
            # Using diskcache
            try:
                return self.cache.delete(key)
            except Exception as e:
                logger.error(f"Error deleting from cache: {e}")
                return False
        else:
            # Using simple file-based cache
            try:
                cache_path = self._get_cache_path(key)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    return True
                return False
            except Exception as e:
                logger.error(f"Error deleting from cache: {e}")
                return False
    
    def clear(self) -> bool:
        """
        Clear the cache.
        
        Returns:
            True if successful, False otherwise
        """
        if self.disable_cache:
            return False
        
        if self.cache:
            # Using diskcache
            try:
                self.cache.clear()
                return True
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
                return False
        else:
            # Using simple file-based cache
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, filename))
                return True
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
                return False
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if self.disable_cache:
            return {'enabled': False}
        
        if self.cache:
            # Using diskcache
            try:
                stats = self.cache.stats()
                return {
                    'enabled': True,
                    'hits': stats.get('hits', 0),
                    'misses': stats.get('misses', 0),
                    'size': self.cache.volume(),
                    'count': len(self.cache)
                }
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
                return {'enabled': True, 'error': str(e)}
        else:
            # Using simple file-based cache
            try:
                files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
                size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
                return {
                    'enabled': True,
                    'count': len(files),
                    'size': size
                }
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
                return {'enabled': True, 'error': str(e)}
    
    def close(self) -> None:
        """Close the cache."""
        if not self.disable_cache and self.cache:
            try:
                self.cache.close()
            except Exception as e:
                logger.error(f"Error closing cache: {e}")
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()


def cached(
    cache: ScraperCache,
    key_prefix: str,
    expiration: Optional[int] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for caching function results.
    
    Args:
        cache: Cache instance
        key_prefix: Prefix for cache keys
        expiration: Cache expiration time in seconds
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # Generate a cache key from function name, args, and kwargs
            key_parts = [key_prefix, func.__name__]
            
            # Add args to key
            for arg in args:
                key_parts.append(str(arg))
            
            # Add kwargs to key (sorted for consistency)
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expiration)
            
            return result
        
        return wrapper
    
    return decorator
