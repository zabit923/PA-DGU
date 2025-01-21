import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from core.database import get_async_session, get_test_async_session, test_engine
from core.database.models import Base


@pytest_asyncio.fixture(scope="function")
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session(init_db) -> AsyncSession:
    async for session in get_test_async_session():
        try:
            yield session
        except IntegrityError:
            await session.rollback()
            raise
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(init_db) -> AsyncClient:
    async def override_get_async_session():
        async for session in get_test_async_session():
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://testserver/api/v1")
    yield client
    await client.aclose()


async def user_authentication_headers(
    client: AsyncClient, username: str, password: str
):
    json = {"username": username, "password": password}
    response = await client.post("/users/login", json=json)
    data = response.json()
    auth_token = data["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
