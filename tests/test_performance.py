import pytest
import asyncio
import time
from httpx import AsyncClient
from app.main import app

pytestmark = pytest.mark.asyncio

class TestPerformance:
    
    async def test_api_response_time(self, client: AsyncClient):
        start = time.time()
        response = await client.get("/health")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 100  # should respond within 100ms
    
    async def test_music_list_performance(self, client: AsyncClient):
        start = time.time()
        response = await client.get("/api/music/")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 200
    
    async def test_concurrent_requests(self, client: AsyncClient):
        async def make_request():
            return await client.get("/health")
        
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        assert all(r.status_code == 200 for r in results)
