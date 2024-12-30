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
async def test_login_user(test_client: AsyncClient, test_session: AsyncSession):
    user = UserFactory(
        username="testlogin", email="testlogin@example.com", is_active=True
    )
    test_session.add(user)
    await test_session.commit()

    response = await test_client.post(
        "/users/login",
        json={"username": "testlogin", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_activate_user(test_client: AsyncClient, test_session: AsyncSession):
    user = UserFactory(is_active=False)
    test_session.add(user)
    await test_session.commit()

    response = await test_client.get(f"/users/activate/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User successfully activated."


@pytest.mark.asyncio
async def test_get_me(test_client: AsyncClient, test_session: AsyncSession):
    user = UserFactory(username="testgetme", email="testgetme@example.com")
    test_session.add(user)
    await test_session.commit()

    login_response = await test_client.post(
        "/users/login",
        json={"username": "testgetme", "password": "password123"},
    )
    access_token = login_response.json()["access_token"]

    response = await test_client.get(
        "/users/get-me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testgetme"
    assert data["email"] == "testgetme@example.com"
