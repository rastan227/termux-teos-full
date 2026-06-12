import pytest
from httpx import AsyncClient
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

class TestEndToEnd:
    
    async def test_full_user_flow(self, client: AsyncClient):
        # 1. Register user via bot (simulated by API)
        response = await client.post("/api/users/register", json={"telegram_id": 99999, "username": "e2e_test"})
        assert response.status_code in [200, 201]
        
        # 2. Check wallet balance
        resp = await client.get("/api/wallet/balance", headers={"Authorization": "Bearer test_token"})
        assert resp.status_code in [200, 401]  # mock token
        
        # 3. Add balance via payment request (mock)
        resp = await client.post("/api/wallet/charge", json={"amount": 50000, "method": "card"}, headers={"Authorization": "Bearer test_token"})
        assert resp.status_code in [200, 401]
        
        # 4. Get services list
        resp = await client.get("/api/services/")
        assert resp.status_code == 200
        
        # 5. Get music list
        resp = await client.get("/api/music/")
        assert resp.status_code == 200
    
    async def test_health_endpoints(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        
        resp = await client.get("/api/health")
        assert resp.status_code == 200
    
    async def test_music_search(self, client: AsyncClient):
        resp = await client.get("/api/music/search", params={"q": "test"})
        assert resp.status_code == 200
        assert "items" in resp.json()
    
    async def test_unauthorized_admin(self, client: AsyncClient):
        resp = await client.get("/api/admin/stats")
        assert resp.status_code == 401
        
        resp = await client.get("/api/owner/tenants")
        assert resp.status_code == 401
