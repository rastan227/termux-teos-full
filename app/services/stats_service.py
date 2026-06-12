import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from app.core.database import async_session_maker
from app.models.user import User
from app.models.music import Music, MusicPlay
from app.models.order import Order
from app.models.transaction import Transaction
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

class StatsService:
    
    @staticmethod
    async def get_daily_stats(date: datetime = None) -> Dict[str, Any]:
        if date is None:
            date = datetime.utcnow().date()
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        async with async_session_maker() as session:
            new_users = await session.execute(
                select(func.count()).where(and_(User.created_at >= start, User.created_at <= end))
            )
            new_orders = await session.execute(
                select(func.count()).where(and_(Order.created_at >= start, Order.created_at <= end))
            )
            revenue = await session.execute(
                select(func.sum(Transaction.amount)).where(
                    and_(Transaction.type == "deposit", Transaction.status == "completed",
                         Transaction.created_at >= start, Transaction.created_at <= end)
                )
            )
            plays = await session.execute(
                select(func.count()).where(and_(MusicPlay.played_at >= start, MusicPlay.played_at <= end))
            )
            
            return {
                "date": date.isoformat(),
                "new_users": new_users.scalar() or 0,
                "new_orders": new_orders.scalar() or 0,
                "revenue": revenue.scalar() or 0,
                "music_plays": plays.scalar() or 0
            }
    
    @staticmethod
    async def get_user_retention(days: int = 30) -> Dict[str, Any]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User.created_at, func.count(User.id)).group_by(func.date(User.created_at)).limit(30)
            )
            rows = result.all()
            return {"data": [{"date": str(r[0]), "count": r[1]} for r in rows]}
    
    @staticmethod
    async def get_top_services(limit: int = 10) -> List[Dict]:
        async with async_session_maker() as session:
            stmt = select(Order.service_id, func.count(Order.id).label("count")).group_by(Order.service_id).order_by(func.count().desc()).limit(limit)
            result = await session.execute(stmt)
            return [{"service_id": r[0], "order_count": r[1]} for r in result]
    
    @staticmethod
    async def get_top_songs(limit: int = 10) -> List[Dict]:
        async with async_session_maker() as session:
            stmt = select(Music.id, Music.title, Music.artist, Music.plays).order_by(Music.plays.desc()).limit(limit)
            result = await session.execute(stmt)
            return [{"id": r[0], "title": r[1], "artist": r[2], "plays": r[3]} for r in result]
    
    @staticmethod
    async def get_system_metrics() -> Dict[str, Any]:
        cpu_usage = await redis_client.get("metric:cpu_usage") or 0
        memory_usage = await redis_client.get("metric:memory_usage") or 0
        return {
            "cpu_usage_percent": float(cpu_usage),
            "memory_usage_mb": float(memory_usage),
            "active_users_today": await redis_client.get("metric:active_users_today") or 0,
            "total_api_requests_today": await redis_client.get("metric:api_requests_today") or 0
        }
