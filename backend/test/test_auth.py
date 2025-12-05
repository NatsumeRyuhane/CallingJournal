"""Tests for authentication functionality."""
import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_register_user(override_get_db):
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
                "phone_number": "+1234567890"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data


@pytest.mark.asyncio
async def test_login_user(override_get_db):
    """Test user login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # Login
        response = await client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(override_get_db):
    """Test getting current user info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        login_response = await client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
