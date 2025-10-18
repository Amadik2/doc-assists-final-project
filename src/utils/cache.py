"""Caching utilities for Doc Assist."""

import functools
import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional, Tuple


class LRUCache:
    """
    Simple LRU cache implementation.
    """
    
    def __init__(self, capacity: int = 100):
        """
        Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items to store
        """
        self.capacity = capacity
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            value, _ = self.cache[key]
            # Update timestamp
            self.cache[key] = (value, time.time())
            self.hits += 1
            return value
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        """
        Put a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Add or update item
        self.cache[key] = (value, time.time())
        
        # Evict if over capacity
        if len(self.cache) > self.capacity:
            # Find oldest item
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of statistics
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }


def memoize(func: Callable) -> Callable:
    """
    Decorator to memoize a function.
    
    Args:
        func: Function to memoize
        
    Returns:
        Memoized function
    """
    cache = LRUCache()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a key from the function name and arguments
        key_parts = [func.__name__]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
        
        # Check cache
        result = cache.get(key)
        if result is not None:
            return result
        
        # Compute and cache result
        result = func(*args, **kwargs)
        cache.put(key, result)
        return result
    
    # Add stats method to the wrapper
    wrapper.cache_stats = cache.get_stats
    
    return wrapper
