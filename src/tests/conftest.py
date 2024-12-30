import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from core.database import get_async_session, get_test_async_session, test_engine
from core.database.models import Base


@pytest.fixture(scope="function")
async def test_client() -> AsyncClient:
    app.dependency_overrides[get_async_session] = get_test_async_session
    async with AsyncClient(app=app, base_url="http://testserver/api/v1") as client:
        yield client


@pytest.fixture(scope="function")
async def test_session() -> AsyncSession:
    async for session in get_test_async_session():
        yield session


@pytest.fixture(scope="function", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
