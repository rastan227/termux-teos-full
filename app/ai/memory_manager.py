from typing import Dict, Any, List, Optional
from app.core.redis_client import redis_client
from app.models.ai_memory import AIMemory, AIInteraction
from app.core.database import async_session_maker
from datetime import datetime, timedelta
import json

class MemoryManager:
    """Short-term and long-term memory management for AI"""
    
    async def get_user_memory(self, user_id: int, session_context: Dict = None) -> Dict:
        """Retrieve user memory from Redis and database"""
        # Short-term from Redis
        short_term_key = f"memory:short:{user_id}"
        short_term = await redis_client.get(short_term_key)
        short_term = json.loads(short_term) if short_term else {}
        
        # Long-term from DB
        async with async_session_maker() as session:
            from sqlalchemy import select
            stmt = select(AIMemory).where(
                AIMemory.user_id == user_id,
                AIMemory.memory_type == "long_term"
            ).limit(20)
            result = await session.execute(stmt)
            memories = result.scalars().all()
            long_term = {m.key: m.value for m in memories}
        
        return {
            "short_term": short_term,
            "long_term": long_term,
            "context": session_context or {}
        }
    
    async def store_interaction(self, user_id: int, user_message: str, ai_response: str, intent: str, confidence: float):
        """Store interaction in database for long-term learning"""
        async with async_session_maker() as session:
            interaction = AIInteraction(
                user_id=user_id,
                user_message=user_message,
                ai_response=ai_response,
                intent=intent,
                confidence=confidence,
                response_time_ms=0,
                tokens_used=0
            )
            session.add(interaction)
            await session.commit()
    
    async def store_short_term(self, user_id: int, key: str, value: str, ttl_seconds: int = 3600):
        """Store temporary memory in Redis"""
        key_full = f"memory:short:{user_id}"
        existing = await redis_client.get(key_full)
        data = json.loads(existing) if existing else {}
        data[key] = value
        await redis_client.setex(key_full, ttl_seconds, json.dumps(data))
    
    async def store_long_term(self, user_id: int, key: str, value: str):
        """Store permanent memory in database"""
        async with async_session_maker() as session:
            memory = AIMemory.create_long_term(user_id, key, value)
            session.add(memory)
            await session.commit()
    
    async def get_total_entries(self) -> int:
        async with async_session_maker() as session:
            from sqlalchemy import func, select
            result = await session.execute(select(func.count()).select_from(AIMemory))
            return result.scalar() or 0
