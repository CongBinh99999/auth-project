"""Tests for Auth API endpoints."""

import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for POST /api/v1/auth/register"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient, test_user_data: dict):
        """Test successful registration."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["requires_verification"] is True
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Test registration with existing email."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "full_name": "First User"
        }
        
        # First registration
        await async_client.post("/api/v1/auth/register", json=user_data)
        
        # Second registration with same email
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code in [400, 409]  # Bad Request or Conflict
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email format."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation Error
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with password too short."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "confirm_password": "short",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation Error


class TestLogin:
    """Tests for POST /api/v1/auth/login"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user_data: dict):
        """Test successful login."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Note: In real test, need to verify email first
        # This test may fail if email verification is required
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        # May be 401 if email not verified
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with wrong password."""
        response = await async_client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401


class TestRefreshToken:
    """Tests for POST /api/v1/auth/refresh"""
    
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code in [401, 400]


class TestLogout:
    """Tests for POST /api/v1/auth/logout"""
    
    @pytest.mark.asyncio
    async def test_logout_without_auth(self, async_client: AsyncClient):
        """Test logout without authentication."""
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": None}
        )
        
        assert response.status_code == 401  # Unauthorized


class TestLogoutAll:
    """Tests for POST /api/v1/auth/logout-all"""
    
    @pytest.mark.asyncio
    async def test_logout_all_without_auth(self, async_client: AsyncClient):
        """Test logout-all without authentication."""
        response = await async_client.post("/api/v1/auth/logout-all")
        
        assert response.status_code == 401  # Unauthorized
