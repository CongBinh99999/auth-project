"""Pytest Configuration - Fixtures for testing.

Contains:
- async_client: AsyncClient for testing FastAPI endpoints
  Tests against directly running server baseURL
"""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.config.settings import get_settings

settings = get_settings()

# Base URL of running server
BASE_URL = "http://localhost:8000"


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Get async test client for running server."""
    async with AsyncClient(base_url=BASE_URL) as client:
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
    """Get authorization headers with valid token.
    
    Note: This may fail if email verification is required.
    """
    # Register user first
    await async_client.post(
        "/api/v1/auth/register",
        json=test_user_data
    )
    
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
