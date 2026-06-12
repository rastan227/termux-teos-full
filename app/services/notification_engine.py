import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from app.core.redis_client import redis_client
from app.core.database import async_session_maker
from app.models.user import User
from app.services.email_service import EmailService
from app.services.sms_service import SmsService
from aiogram import Bot
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(str, Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"

@dataclass
class Notification:
    user_id: int
    title: str
    message: str
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.NORMAL
    template_name: Optional[str] = None
    template_data: Optional[Dict] = None
    scheduled_for: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

class NotificationEngine:
    _bot: Bot = None
    
    @classmethod
    def init_bot(cls, bot: Bot):
        cls._bot = bot
    
    @classmethod
    async def send(cls, notification: Notification) -> bool:
        if notification.scheduled_for and notification.scheduled_for > datetime.utcnow():
            # Schedule for later using Redis
            delay = (notification.scheduled_for - datetime.utcnow()).total_seconds()
            await cls._schedule_delayed(notification, delay)
            return True
        
        return await cls._send_immediate(notification)
    
    @classmethod
    async def _send_immediate(cls, notification: Notification) -> bool:
        try:
            if notification.channel == NotificationChannel.TELEGRAM:
                return await cls._send_telegram(notification)
            elif notification.channel == NotificationChannel.EMAIL:
                return await cls._send_email(notification)
            elif notification.channel == NotificationChannel.SMS:
                return await cls._send_sms(notification)
            else:
                logger.warning(f"Unknown channel: {notification.channel}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            if notification.retry_count < notification.max_retries:
                notification.retry_count += 1
                await asyncio.sleep(2 ** notification.retry_count)
                return await cls._send_immediate(notification)
            return False
    
    @classmethod
    async def _send_telegram(cls, notification: Notification) -> bool:
        if not cls._bot:
            logger.error("Bot not initialized")
            return False
        try:
            text = cls._render_message(notification)
            await cls._bot.send_message(notification.user_id, text, parse_mode="HTML")
            logger.info(f"Telegram notification sent to {notification.user_id}")
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    @classmethod
    async def _send_email(cls, notification: Notification) -> bool:
        user = await cls._get_user(notification.user_id)
        if not user or not user.email:
            return False
        subject = notification.title
        body = cls._render_message(notification)
        return await EmailService.send_email(user.email, subject, body, html=False)
    
    @classmethod
    async def _send_sms(cls, notification: Notification) -> bool:
        user = await cls._get_user(notification.user_id)
        if not user or not user.phone:
            return False
        message = cls._render_message(notification)
        return await SmsService.send_sms(user.phone, message[:160])  # SMS length limit
    
    @classmethod
    def _render_message(cls, notification: Notification) -> str:
        if notification.template_name:
            # Load template from DB or file
            templates = {
                "order_confirmed": "✅ سفارش شما با شماره {order_id} تأیید شد.",
                "wallet_credited": "💰 {amount} تومان به کیف پول شما اضافه شد. موجودی: {balance}",
                "ticket_replied": "🎫 تیکت شما پاسخ داده شد: {ticket_number}",
            }
            template = templates.get(notification.template_name, notification.message)
            if notification.template_data:
                return template.format(**notification.template_data)
        return notification.message
    
    @classmethod
    async def _schedule_delayed(cls, notification: Notification, delay_seconds: float):
        key = f"notification:scheduled:{notification.user_id}:{datetime.utcnow().timestamp()}"
        await redis_client.setex(key, int(delay_seconds), json.dumps({
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
            "channel": notification.channel.value,
            "priority": notification.priority.value,
            "template_name": notification.template_name,
            "template_data": notification.template_data
        }))
    
    @classmethod
    async def _get_user(cls, user_id: int):
        async with async_session_maker() as session:
            from sqlalchemy import select
            from app.models.user import User
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            return result.scalar_one_or_none()
    
    @classmethod
    async def broadcast_to_role(cls, role: str, title: str, message: str, channel: NotificationChannel = NotificationChannel.TELEGRAM):
        async with async_session_maker() as session:
            from sqlalchemy import select
            from app.models.user import User, UserRole
            stmt = select(User.telegram_id).where(User.role == UserRole(role))
            result = await session.execute(stmt)
            user_ids = result.scalars().all()
            for uid in user_ids:
                await cls.send(Notification(
                    user_id=uid,
                    title=title,
                    message=message,
                    channel=channel,
                    priority=NotificationPriority.HIGH
                ))
            logger.info(f"Broadcast to {len(user_ids)} users with role {role}")
