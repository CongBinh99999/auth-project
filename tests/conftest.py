"""Pytest Configuration - Fixtures for testing.

Contains:
- async_client: AsyncClient chạy thẳng vào ASGI app, không cần server ngoài.
"""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.config.database import AsyncSessionLocal
from app.main import app
from app.repositories.user_repository import UserRepository

# httpx cần một base_url hợp lệ; không có request nào ra mạng thật.
BASE_URL = "http://test"


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Client gọi trực tiếp vào ASGI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=BASE_URL
    ) as client:
        yield client


@pytest.fixture
def test_user_data() -> dict:
    """Test user data - unique email for each test."""
    password = "TestPassword123!"
    return {
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": password,
        "confirm_password": password,
        "full_name": "Test User"
    }


@pytest.fixture
async def registered_user(async_client: AsyncClient, test_user_data: dict) -> dict:
    """Create a test user via API."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json=test_user_data
    )
    if response.status_code == 201:
        return {
            **response.json(),
            "password": test_user_data["password"],
            "email": test_user_data["email"]
        }
    return test_user_data


@pytest.fixture
async def auth_headers(async_client: AsyncClient, test_user_data: dict) -> dict:
    """Get authorization headers with valid token."""
    # Register user first
    await async_client.post(
        "/api/v1/auth/register",
        json=test_user_data
    )

    # Login chặn user chưa verify. Token xác thực chỉ tồn tại trong email nên
    # test đánh dấu verified thẳng qua repository.
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(test_user_data["email"])
        if user:
            await user_repo.verify_by_id(user.id)
            await session.commit()
    
    # Try to login (may fail if email not verified)
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return {}
