from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar

from app.core.connections import BaseClient, BaseContextManager

T = TypeVar("T")


@asynccontextmanager
async def managed_client(client: BaseClient) -> AsyncGenerator[T, None]:
    connection = None
    try:
        connection = await client.connect()
        yield connection
    finally:
        await client.close()


@asynccontextmanager
async def managed_context(
    context_manager: BaseContextManager,
) -> AsyncGenerator[T, None]:
    async with context_manager as connection:
        yield connection
