"""Tests for Devices API endpoints."""

import pytest
from uuid import uuid4
from httpx import AsyncClient


class TestGetMyDevices:
    """Tests for GET /api/v1/devices/"""
    
    @pytest.mark.asyncio
    async def test_get_devices_without_auth(self, async_client: AsyncClient):
        """Test get devices without authentication."""
        response = await async_client.get("/api/v1/devices/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_devices_with_auth(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test get devices with valid token."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.get(
            "/api/v1/devices/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert "total_count" in data


class TestGetDevice:
    """Tests for GET /api/v1/devices/{device_id}"""
    
    @pytest.mark.asyncio
    async def test_get_device_without_auth(self, async_client: AsyncClient):
        """Test get single device without authentication."""
        device_id = uuid4()
        response = await async_client.get(f"/api/v1/devices/{device_id}")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_device_not_found(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test get non-existent device."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        device_id = uuid4()
        response = await async_client.get(
            f"/api/v1/devices/{device_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestUpdateDevice:
    """Tests for PATCH /api/v1/devices/{device_id}"""
    
    @pytest.mark.asyncio
    async def test_update_device_without_auth(self, async_client: AsyncClient):
        """Test update device without authentication."""
        device_id = uuid4()
        response = await async_client.patch(
            f"/api/v1/devices/{device_id}",
            json={"device_name": "My Phone"}
        )
        
        assert response.status_code == 401


class TestTrustDevice:
    """Tests for POST /api/v1/devices/{device_id}/trust"""
    
    @pytest.mark.asyncio
    async def test_trust_device_without_auth(self, async_client: AsyncClient):
        """Test trust device without authentication."""
        device_id = uuid4()
        response = await async_client.post(f"/api/v1/devices/{device_id}/trust")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_trust_device_not_found(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test trust non-existent device."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        device_id = uuid4()
        response = await async_client.post(
            f"/api/v1/devices/{device_id}/trust",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestUntrustDevice:
    """Tests for DELETE /api/v1/devices/{device_id}/trust"""
    
    @pytest.mark.asyncio
    async def test_untrust_device_without_auth(self, async_client: AsyncClient):
        """Test untrust device without authentication."""
        device_id = uuid4()
        response = await async_client.delete(f"/api/v1/devices/{device_id}/trust")
        
        assert response.status_code == 401


class TestRemoveDevice:
    """Tests for DELETE /api/v1/devices/{device_id}"""
    
    @pytest.mark.asyncio
    async def test_remove_device_without_auth(self, async_client: AsyncClient):
        """Test remove device without authentication."""
        device_id = uuid4()
        response = await async_client.delete(f"/api/v1/devices/{device_id}")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_remove_device_not_found(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test remove non-existent device."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        device_id = uuid4()
        response = await async_client.delete(
            f"/api/v1/devices/{device_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestRemoveAllDevices:
    """Tests for DELETE /api/v1/devices/"""
    
    @pytest.mark.asyncio
    async def test_remove_all_devices_without_auth(self, async_client: AsyncClient):
        """Test remove all devices without authentication."""
        response = await async_client.delete("/api/v1/devices/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_remove_all_devices_with_auth(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test remove all devices with valid token."""
        if not auth_headers:
            pytest.skip("Could not get auth headers")
        
        response = await async_client.delete(
            "/api/v1/devices/",
            headers=auth_headers
        )
        
        assert response.status_code == 204
