from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
import hashlib
import json
import time


class CacheManager:
    """简单的内存缓存管理器"""

    def __init__(self, default_ttl: int = 300):
        """
        初始化缓存管理器

        Args:
            default_ttl: 默认缓存过期时间（秒）
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """
        生成缓存键

        Args:
            func_name: 函数名
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            缓存键
        """
        key_parts = [func_name]
        
        for arg in args:
            if hasattr(arg, '__class__'):
                key_parts.append(f"{arg.__class__.__name__}")
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        if key in self._cache:
            value, expiry_time = self._cache[key]
            if time.time() < expiry_time:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果为None则使用默认值
        """
        expiry_time = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = (value, expiry_time)

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()

    def delete(self, key: str) -> bool:
        """
        删除指定缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def cleanup_expired(self) -> int:
        """
        清理过期的缓存

        Returns:
            清理的缓存数量
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items()
            if current_time >= expiry_time
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)


def cached(ttl: int = 300, cache_manager: Optional[CacheManager] = None):
    """
    缓存装饰器

    Args:
        ttl: 缓存过期时间（秒）
        cache_manager: 缓存管理器实例，如果为None则使用默认实例

    Returns:
        装饰器函数
    """
    if cache_manager is None:
        cache_manager = CacheManager(default_ttl=ttl)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            cache_key = cache_manager._generate_key(func_name, *args, **kwargs)
            
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


# 全局缓存管理器实例
cache_manager = CacheManager(default_ttl=300)  # 默认5分钟缓存
