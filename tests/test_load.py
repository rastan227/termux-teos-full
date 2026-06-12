import pytest
import asyncio
import aiohttp
import time
from app.core.config import settings

pytestmark = pytest.mark.asyncio

class TestLoad:
    
    async def test_high_concurrency_music(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(100):
                tasks.append(session.get(f"http://localhost:8000/api/music/"))
            start = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start
            success = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            assert success > 90  # at least 90% success
            print(f"Load test: {success} successful, elapsed {elapsed:.2f}s")
