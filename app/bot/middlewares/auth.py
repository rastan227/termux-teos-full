from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        user = await UserService.get_user_by_telegram_id(user_id)
        if not user:
            user = await UserService.get_or_create(user_id, event.from_user.username, event.from_user.first_name)
        data['user'] = user
        return await handler(event, data)
