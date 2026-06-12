import pytest
from httpx import AsyncClient
from app.main import app

pytestmark = pytest.mark.asyncio

class TestAPIAuth:
    
    async def test_health_public(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
    
    async def test_api_health_public(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200
    
    async def test_music_list_public(self, client: AsyncClient):
        response = await client.get("/api/music/")
        assert response.status_code == 200
    
    async def test_protected_endpoint_no_token(self, client: AsyncClient):
        response = await client.get("/api/admin/stats")
        assert response.status_code == 401
        
        response = await client.get("/api/owner/tenants")
        assert response.status_code == 401
    
    async def test_invalid_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/admin/stats", headers=headers)
        assert response.status_code == 401
    
    async def test_wallet_balance_unauth(self, client: AsyncClient):
        response = await client.get("/api/wallet/balance")
        assert response.status_code == 401
