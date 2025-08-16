import logging
from typing import List, Optional

from redis import Redis


class BaseRedisDataManager:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.logger = logging.getLogger(self.__class__.__name__)

    async def set(self, key: str, value: str, expires: Optional[int] = None) -> None:
        self.redis.set(key, value, ex=expires)

    async def get(self, key: str) -> Optional[str]:
        result = self.redis.get(key)
        return result.decode() if result else None

    async def delete(self, key: str) -> None:
        self.redis.delete(key)

    async def sadd(self, key: str, value: str) -> None:
        self.redis.sadd(key, value)

    async def srem(self, key: str, value: str) -> None:
        self.redis.srem(key, value)

    async def keys(self, pattern: str) -> List[bytes]:
        return self.redis.keys(pattern)

    async def smembers(self, key: str) -> List[str]:
        result = self.redis.smembers(key)
        return [member.decode() for member in result] if result else []

    async def sismember(self, key: str, value: str) -> bool:
        return bool(self.redis.sismember(key, value))

    async def set_expire(self, key: str, seconds: int) -> None:
        self.redis.expire(key, seconds)
