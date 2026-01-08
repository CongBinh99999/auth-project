"""Tests for Users API endpoints."""

import pytest
from httpx import AsyncClient


class TestGetMyProfile:
    """Tests for GET /api/v1/users/me"""
    
    @pytest.mark.asyncio
    async def test_get_profile_without_auth(self, async_client: AsyncClient):
        """Test get profile without authentication."""
        response = await async_client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_profile_with_auth(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test get profile with valid token."""
        if not auth_headers:
            pytest.skip("Could not get auth headers (user not verified)")
        
        response = await async_client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data


class TestUpdateMyProfile:
    """Tests for PATCH /api/v1/users/me"""
    
    @pytest.mark.asyncio
    async def test_update_profile_without_auth(self, async_client: AsyncClient):
        """Test update profile without authentication."""
        response = await async_client.patch(
            "/api/v1/users/me",
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_profile_with_auth(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test update profile with valid token."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"


class TestChangePassword:
    """Tests for PATCH /api/v1/users/me/password"""
    
    @pytest.mark.asyncio
    async def test_change_password_without_auth(self, async_client: AsyncClient):
        """Test change password without authentication."""
        response = await async_client.patch(
            "/api/v1/users/me/password",
            json={
                "old_password": "oldpass123",
                "new_password": "newpass123",
                "confirm_password": "newpass123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_change_password_mismatch(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test change password with mismatched confirmation."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.patch(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={
                "old_password": "TestPassword123!",
                "new_password": "newpass123",
                "confirm_password": "differentpass"
            }
        )
        
        assert response.status_code == 422  # Validation error
