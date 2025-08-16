from typing import AsyncGenerator

from app.core.connections.storage import S3ContextManager
from app.core.dependencies.base import managed_context

_s3_context = S3ContextManager()


async def get_s3_client() -> AsyncGenerator:
    async with managed_context(_s3_context) as s3:
        yield s3
