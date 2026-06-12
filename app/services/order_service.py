import logging
from typing import Optional, Dict, Any, List
from sqlalchemy import select, update, func
from app.core.database import async_session_maker
from app.models.order import Order, OrderStatus
from app.models.service import Service
from app.services.wallet_service import WalletService
from app.services.notification_engine import NotificationEngine, Notification, NotificationChannel, NotificationPriority
from datetime import datetime, timedelta
import json
import secrets

logger = logging.getLogger(__name__)

class OrderService:
    
    @staticmethod
    def generate_order_number() -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"ORD-{timestamp}-{random_part}"
    
    @staticmethod
    async def create_order(user_id: int, service_id: int, quantity: int = 1) -> Optional[Order]:
        async with async_session_maker() as session:
            service = await session.get(Service, service_id)
            if not service or not service.is_active:
                return None
            
            total = service.price * quantity
            if not await WalletService.deduct_balance(user_id, total, f"Purchase of {service.name}"):
                return None
            
            order = Order(
                order_number=OrderService.generate_order_number(),
                user_id=user_id,
                service_id=service_id,
                quantity=quantity,
                unit_price=service.price,
                total_price=total,
                discount=0,
                final_price=total,
                period=service.period.value,
                status=OrderStatus.PAID,
                payment_status="paid"
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            
            # Auto-deliver if applicable
            await OrderService.deliver_order(order.id)
            return order
    
    @staticmethod
    async def deliver_order(order_id: int) -> bool:
        async with async_session_maker() as session:
            order = await session.get(Order, order_id)
            if not order or order.status != OrderStatus.PAID:
                return False
            
            service = await session.get(Service, order.service_id)
            if not service:
                return False
            
            delivery_info = {
                "service_type": service.type.value,
                "credentials": f"user_{order.user_id}_vpn_config",
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
            }
            order.delivery_data = delivery_info
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
            await session.commit()
            
            await NotificationEngine.send(Notification(
                user_id=order.user_id,
                title="سرویس فعال شد",
                message=f"🎉 سرویس {service.name} با موفقیت فعال شد.\nاطلاعات: {json.dumps(delivery_info)}",
                channel=NotificationChannel.TELEGRAM,
                priority=NotificationPriority.HIGH
            ))
            return True
    
    @staticmethod
    async def update_delivery_data(order_id: int, credentials: dict) -> bool:
        async with async_session_maker() as session:
            order = await session.get(Order, order_id)
            if not order:
                return False
            order.delivery_data = credentials
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
            await session.commit()
            return True
    
    @staticmethod
    async def get_user_orders(user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        async with async_session_maker() as session:
            offset = (page - 1) * limit
            count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
            total = await session.execute(count_stmt)
            total = total.scalar()
            
            stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()).offset(offset).limit(limit)
            result = await session.execute(stmt)
            orders = result.scalars().all()
            return {
                "items": [o.to_dict() for o in orders],
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
