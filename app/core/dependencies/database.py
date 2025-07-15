from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.database import DatabaseClient

database_client = DatabaseClient()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = await database_client.connect()

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
