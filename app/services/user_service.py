import logging
import random
import string
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.user import User, UserRole, UserStatus
from app.models.audit_log import AuditLog
from app.core.security import hash_password, verify_password
from app.core.config import settings

logger = logging.getLogger(__name__)

class UserService:
    
    @staticmethod
    async def get_or_create(telegram_id: int, username: Optional[str], first_name: str, last_name: Optional[str] = None) -> User:
        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Update existing user info
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                user.last_seen = func.now()
                await session.commit()
                return user
            
            # Create new user
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                referral_code=referral_code,
                language="fa"
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info(f"New user created: {telegram_id}")
            return new_user
    
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        async with async_session_maker() as session:
            return await session.get(User, user_id)
    
    @staticmethod
    async def update_user(telegram_id: int, data: Dict[str, Any]) -> Optional[User]:
        async with async_session_maker() as session:
            user = await UserService.get_user_by_telegram_id(telegram_id)
            if not user:
                return None
            for key, value in data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def change_role(telegram_id: int, new_role: UserRole, changed_by: int) -> bool:
        async with async_session_maker() as session:
            user = await UserService.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            old_role = user.role
            user.role = new_role
            await session.commit()
            
            # Log audit
            audit = AuditLog.create(
                user_id=changed_by,
                action="change_user_role",
                resource_type="user",
                resource_id=telegram_id,
                old_value={"role": old_role.value},
                new_value={"role": new_role.value}
            )
            session.add(audit)
            await session.commit()
            logger.info(f"User {telegram_id} role changed from {old_role} to {new_role} by {changed_by}")
            return True
    
    @staticmethod
    async def ban_user(telegram_id: int, reason: str, banned_by: int) -> bool:
        async with async_session_maker() as session:
            user = await UserService.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            user.ban(reason, banned_by)
            await session.commit()
            
            audit = AuditLog.create(
                user_id=banned_by,
                action="ban_user",
                resource_type="user",
                resource_id=telegram_id,
                new_value={"reason": reason}
            )
            session.add(audit)
            await session.commit()
            return True
    
    @staticmethod
    async def unban_user(telegram_id: int, unbanned_by: int) -> bool:
        async with async_session_maker() as session:
            user = await UserService.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            user.unban()
            await session.commit()
            return True
    
    @staticmethod
    async def get_users_by_role(role: UserRole, limit: int = 100, offset: int = 0) -> List[User]:
        async with async_session_maker() as session:
            stmt = select(User).where(User.role == role).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def search_users(query: str, limit: int = 50) -> List[Dict]:
        async with async_session_maker() as session:
            search_term = f"%{query}%"
            stmt = select(User).where(
                or_(
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            ).limit(limit)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return [u.to_dict() for u in users]
    
    @staticmethod
    async def get_user_stats() -> Dict[str, Any]:
        async with async_session_maker() as session:
            total = await session.execute(select(func.count()).select_from(User))
            active = await session.execute(select(func.count()).where(User.is_active == True))
            banned = await session.execute(select(func.count()).where(User.is_banned == True))
            admins = await session.execute(
                select(func.count()).where(User.role.in_([UserRole.MUSIC_ADMIN, UserRole.SERVICE_ADMIN, UserRole.SUPER_ADMIN, UserRole.OWNER]))
            )
            return {
                "total_users": total.scalar() or 0,
                "active_users": active.scalar() or 0,
                "banned_users": banned.scalar() or 0,
                "admin_count": admins.scalar() or 0
            }
    
    @staticmethod
    async def get_referral_info(telegram_id: int) -> Dict:
        user = await UserService.get_user_by_telegram_id(telegram_id)
        if not user:
            return {}
        return {
            "referral_code": user.referral_code,
            "referral_count": user.referral_count,
            "referral_earnings": user.referral_earnings,
        }
    
    @staticmethod
    async def apply_referral(new_user_id: int, referral_code: str) -> bool:
        async with async_session_maker() as session:
            # Find referrer by code
            referrer = await session.execute(
                select(User).where(User.referral_code == referral_code)
            )
            referrer = referrer.scalar_one_or_none()
            if not referrer or referrer.telegram_id == new_user_id:
                return False
            
            new_user = await UserService.get_user_by_telegram_id(new_user_id)
            if not new_user or new_user.referrer_id:
                return False
            
            new_user.referrer_id = referrer.telegram_id
            referrer.referral_count += 1
            # Give bonus to referrer
            bonus = 5000  # configurable
            referrer.add_balance(bonus)
            
            # Create transaction for bonus
            from app.models.transaction import Transaction, TransactionType, TransactionStatus
            tx = Transaction(
                user_id=referrer.telegram_id,
                amount=bonus,
                balance_before=referrer.wallet_balance - bonus,
                balance_after=referrer.wallet_balance,
                type=TransactionType.REFERRAL_BONUS,
                status=TransactionStatus.COMPLETED,
                description=f"Referral bonus for inviting {new_user_id}"
            )
            session.add(tx)
            await session.commit()
            return True
