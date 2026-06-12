import logging
from typing import List, Optional
from aiogram import Bot
from app.core.config import settings
from app.core.database import async_session_maker
from app.models.user import User

logger = logging.getLogger(__name__)
bot = Bot(token=settings.BOT_TOKEN)

class NotificationService:
    
    @staticmethod
    async def notify_user(telegram_id: int, message: str, parse_mode: str = "Markdown"):
        try:
            await bot.send_message(telegram_id, message, parse_mode=parse_mode)
            logger.info(f"Notified user {telegram_id}")
        except Exception as e:
            logger.error(f"Failed to notify user {telegram_id}: {e}")
    
    @staticmethod
    async def notify_admins(message: str):
        for admin_id in settings.ADMIN_IDS:
            await NotificationService.notify_user(admin_id, f"🔔 {message}")
    
    @staticmethod
    async def broadcast_to_role(role: str, message: str, exclude_user_ids: List[int] = None):
        async with async_session_maker() as session:
            from app.models.user import UserRole
            stmt = select(User.telegram_id).where(User.role == role, User.is_active == True)
            result = await session.execute(stmt)
            user_ids = result.scalars().all()
            
            for uid in user_ids:
                if exclude_user_ids and uid in exclude_user_ids:
                    continue
                await NotificationService.notify_user(uid, message)
    
    @staticmethod
    async def broadcast_all(message: str, exclude_bots: bool = True):
        async with async_session_maker() as session:
            stmt = select(User.telegram_id).where(User.is_active == True)
            if exclude_bots:
                stmt = stmt.where(User.username.notilike("%bot%"))
            result = await session.execute(stmt)
            user_ids = result.scalars().all()
            
            for uid in user_ids:
                await NotificationService.notify_user(uid, message)
