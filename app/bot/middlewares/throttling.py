from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.core.redis_client import redis_client
import time
import logging

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 10, period: int = 60):
        self.limit = limit
        self.period = period
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        key = f"throttle:{user_id}"
        current = await redis_client.get(key)
        if current and int(current) >= self.limit:
            await event.answer("⏳ شما بیش از حد درخواست ارسال کرده‌اید. لطفاً چند لحظه صبر کنید.")
            return
        await redis_client.incr(key)
        await redis_client.expire(key, self.period)
        return await handler(event, data)
