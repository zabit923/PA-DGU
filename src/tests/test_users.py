import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.factories import UserFactory


@pytest.mark.asyncio
async def test_register_user(test_client: AsyncClient):
    response = await test_client.post(
        "/users/register",
        data={
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "password": "password123",
            "is_teacher": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_activate_user(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(is_active=False)
    session.add(user)
    await session.commit()

    response = await test_client.get(f"/users/activate/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User successfully activated."


@pytest.mark.asyncio
async def test_login_user(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(
        username="testlogin",
        email="testlogin@example.com",
        is_active=True,
    )
    session.add(user)
    await session.commit()

    response = await test_client.post(
        "/users/login",
        json={"username": "testlogin", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_update_user(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(username="updatableuser", is_active=True)
    session.add(user)
    await session.commit()

    response = await test_client.patch(
        "/users",
        data={"first_name": "UpdatedName"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedName"


@pytest.mark.asyncio
async def test_get_me(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(username="meuser", is_active=True)
    session.add(user)
    await session.commit()

    response = await test_client.get(
        "/users/get-me",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"


@pytest.mark.asyncio
async def test_get_all_users(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    superuser = UserFactory(is_superuser=True)
    session.add(superuser)
    await session.commit()

    response = await test_client.get(
        "/users",
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_user_by_id(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(username="singleuser", is_active=True)
    session.add(user)
    await session.commit()

    response = await test_client.get(
        f"/users/{user.id}",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "singleuser"


@pytest.mark.asyncio
async def test_change_online_status(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(is_online=False, is_active=True)
    session.add(user)
    await session.commit()

    response = await test_client.get(
        "/users/change-online-status",
    )
    assert response.status_code == 200
    data = response.json()
    assert "User status has changed to: {user.is_online}." in data["message"]


@pytest.mark.asyncio
async def test_change_ignore_status(test_client: AsyncClient, session: AsyncSession):
    UserFactory._meta.sqlalchemy_session = session
    user = UserFactory(ignore_messages=False, is_active=True)
    session.add(user)
    await session.commit()

    response = await test_client.get(
        "/users/change-ignore-status",
    )
    assert response.status_code == 200
    data = response.json()
    assert (
        f"User ignore status has changed to: {user.ignore_messages}." in data["message"]
    )
