import logging
from typing import Optional, Dict, Any, List
from sqlalchemy import select, func
from app.core.database import async_session_maker
from app.models.audit_log import AuditLog
from app.core.config import settings
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AuditService:
    
    @staticmethod
    async def log(user_id: int, action: str, resource_type: str = None, resource_id: str = None,
                  old_value: Any = None, new_value: Any = None, ip_address: str = None, 
                  user_agent: str = None, status: str = "success", error: str = None) -> None:
        """Log an audit event"""
        async with async_session_maker() as session:
            audit = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                error_message=error
            )
            session.add(audit)
            await session.commit()
            logger.info(f"Audit: {user_id} - {action} - {status}")
    
    @staticmethod
    async def get_logs(page: int = 1, limit: int = 50, user_id: int = None, action: str = None) -> Dict[str, Any]:
        async with async_session_maker() as session:
            offset = (page - 1) * limit
            query = select(AuditLog)
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            if action:
                query = query.where(AuditLog.action == action)
            
            count_stmt = select(func.count()).select_from(AuditLog)
            if user_id:
                count_stmt = count_stmt.where(AuditLog.user_id == user_id)
            if action:
                count_stmt = count_stmt.where(AuditLog.action == action)
            total = await session.execute(count_stmt)
            total = total.scalar()
            
            query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
            result = await session.execute(query)
            logs = result.scalars().all()
            return {
                "items": [log.to_dict() for log in logs],
                "total": total,
                "page": page
            }
