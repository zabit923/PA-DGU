from typing import AsyncGenerator

from redis import Redis

from app.core.connections import RedisContextManager
from app.core.dependencies import managed_context

_redis_context = RedisContextManager()


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with managed_context(_redis_context) as redis:
        yield redis
