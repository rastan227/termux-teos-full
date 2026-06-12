import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import hmac
from app.core.config import settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

class SecurityService:
    
    # Rate limiting
    @staticmethod
    async def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
        """Returns True if under limit, False if exceeded"""
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, window_seconds)
        return current <= limit
    
    @staticmethod
    async def record_failed_login(telegram_id: int):
        key = f"failed_login:{telegram_id}"
        await redis_client.incr(key)
        await redis_client.expire(key, 3600)
        count = int(await redis_client.get(key) or 0)
        if count >= 5:
            # Temporary lock
            lock_key = f"lockout:{telegram_id}"
            await redis_client.setex(lock_key, 1800, "1")
    
    @staticmethod
    async def is_locked_out(telegram_id: int) -> bool:
        lock_key = f"lockout:{telegram_id}"
        return await redis_client.exists(lock_key)
    
    @staticmethod
    async def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    async def sanitize_input(text: str) -> str:
        """Basic XSS prevention and sanitization"""
        import html
        return html.escape(text.strip())[:2000]
    
    @staticmethod
    async def detect_spam(telegram_id: int, action: str) -> bool:
        """Returns True if spam detected"""
        key = f"spam:{telegram_id}:{action}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 60)
        if count > 10:  # 10 actions per minute
            logger.warning(f"Spam detected from {telegram_id} on {action}")
            return True
        return False
