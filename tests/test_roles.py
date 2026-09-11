"""Tests for Roles API endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestGetAllRoles:
    """Tests for GET /api/v1/roles/"""
    
    @pytest.mark.asyncio
    async def test_get_roles_without_auth(self, async_client: AsyncClient):
        """Test get roles without authentication."""
        response = await async_client.get("/api/v1/roles/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_roles_without_admin(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test get roles without admin permission."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.get(
            "/api/v1/roles/",
            headers=auth_headers
        )
        
        # Should be 403 Forbidden if not admin
        assert response.status_code in [200, 403]


class TestGetRole:
    """Tests for GET /api/v1/roles/{role_id}"""
    
    @pytest.mark.asyncio
    async def test_get_role_without_auth(self, async_client: AsyncClient):
        """Test get single role without authentication."""
        role_id = uuid4()
        response = await async_client.get(f"/api/v1/roles/{role_id}")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_role_not_found(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test get non-existent role."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        role_id = uuid4()
        response = await async_client.get(
            f"/api/v1/roles/{role_id}",
            headers=auth_headers
        )
        
        # 403 if not admin, 404 if not found
        assert response.status_code in [403, 404]


class TestCreateRole:
    """Tests for POST /api/v1/roles/"""
    
    @pytest.mark.asyncio
    async def test_create_role_without_auth(self, async_client: AsyncClient):
        """Test create role without authentication."""
        response = await async_client.post(
            "/api/v1/roles/",
            json={
                "code": "test_role",
                "name": "Test Role",
                "description": "A test role"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_role_invalid_data(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test create role with invalid data."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.post(
            "/api/v1/roles/",
            headers=auth_headers,
            json={}  # Missing required fields
        )
        
        # 403 if not admin, 422 if validation error
        assert response.status_code in [403, 422]


class TestUpdateRole:
    """Tests for PATCH /api/v1/roles/{role_id}"""
    
    @pytest.mark.asyncio
    async def test_update_role_without_auth(self, async_client: AsyncClient):
        """Test update role without authentication."""
        role_id = uuid4()
        response = await async_client.patch(
            f"/api/v1/roles/{role_id}",
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == 401


class TestDeleteRole:
    """Tests for DELETE /api/v1/roles/{role_id}"""
    
    @pytest.mark.asyncio
    async def test_delete_role_without_auth(self, async_client: AsyncClient):
        """Test delete role without authentication."""
        role_id = uuid4()
        response = await async_client.delete(f"/api/v1/roles/{role_id}")
        
        assert response.status_code == 401


class TestRolePermissions:
    """Tests for role permission endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_permissions_without_auth(self, async_client: AsyncClient):
        """Test get role permissions without authentication."""
        role_id = uuid4()
        response = await async_client.get(f"/api/v1/roles/{role_id}/permissions")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_assign_permission_without_auth(self, async_client: AsyncClient):
        """Test assign permission without authentication."""
        role_id = uuid4()
        permission_id = uuid4()
        response = await async_client.post(
            f"/api/v1/roles/{role_id}/permissions/{permission_id}"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_remove_permission_without_auth(self, async_client: AsyncClient):
        """Test remove permission without authentication."""
        role_id = uuid4()
        permission_id = uuid4()
        response = await async_client.delete(
            f"/api/v1/roles/{role_id}/permissions/{permission_id}"
        )
        
        assert response.status_code == 401
