import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from app.core.database import engine
from app.core.redis_client import redis_client
from app.services.system_health import SystemHealth
from app.core.config import settings

logger = logging.getLogger(__name__)

class HealthService:
    
    @staticmethod
    async def check_all() -> Dict[str, Any]:
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check database
        db_status = await HealthService.check_database()
        results["services"]["database"] = db_status
        
        # Check Redis
        redis_status = await HealthService.check_redis()
        results["services"]["redis"] = redis_status
        
        # Check API
        api_status = await HealthService.check_api()
        results["services"]["api"] = api_status
        
        # Overall status
        unhealthy = any(s["status"] != "healthy" for s in results["services"].values())
        results["status"] = "degraded" if unhealthy else "healthy"
        
        return results
    
    @staticmethod
    async def check_database() -> Dict:
        try:
            start = asyncio.get_event_loop().time()
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "down", "error": str(e)}
    
    @staticmethod
    async def check_redis() -> Dict:
        try:
            start = asyncio.get_event_loop().time()
            await redis_client.ping()
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "down", "error": str(e)}
    
    @staticmethod
    async def check_api() -> Dict:
        # Could call internal endpoint
        return {"status": "healthy", "latency_ms": 0}
