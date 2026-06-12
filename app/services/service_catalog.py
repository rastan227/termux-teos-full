import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func, and_
from app.core.database import async_session_maker
from app.models.service import Service, ServiceType, ServicePeriod
from app.models.order import Order, OrderStatus
from app.services.wallet_service import WalletService
import random
import string

logger = logging.getLogger(__name__)

class ServiceCatalogService:
    
    @staticmethod
    async def get_all_services(category: Optional[str] = None, active_only: bool = True) -> List[Service]:
        async with async_session_maker() as session:
            stmt = select(Service)
            if active_only:
                stmt = stmt.where(Service.is_active == True)
            if category:
                stmt = stmt.where(Service.category == category)
            stmt = stmt.order_by(Service.sort_order)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    @staticmethod
    async def get_service_by_id(service_id: int) -> Optional[Service]:
        async with async_session_maker() as session:
            return await session.get(Service, service_id)
    
    @staticmethod
    async def create_service(data: Dict[str, Any]) -> Service:
        async with async_session_maker() as session:
            slug = data.get("slug") or data["name"].lower().replace(" ", "-")
            service = Service(
                name=data["name"],
                slug=slug,
                description=data.get("description"),
                type=data.get("type", ServiceType.OTHER),
                category=data.get("category"),
                price=data["price"],
                compare_price=data.get("compare_price"),
                period=data.get("period", ServicePeriod.MONTHLY),
                setup_fee=data.get("setup_fee", 0),
                spec_data=data.get("spec_data"),
                location=data.get("location"),
                stock=data.get("stock", -1),
                delivery_type=data.get("delivery_type", "auto"),
                delivery_webhook=data.get("delivery_webhook"),
                max_per_user=data.get("max_per_user", 1),
                trial_available=data.get("trial_available", False),
                trial_days=data.get("trial_days", 0),
                is_featured=data.get("is_featured", False),
                sort_order=data.get("sort_order", 0),
                image_url=data.get("image_url"),
                tags=data.get("tags"),
            )
            session.add(service)
            await session.commit()
            await session.refresh(service)
            return service
    
    @staticmethod
    async def update_service(service_id: int, data: Dict[str, Any]) -> Optional[Service]:
        async with async_session_maker() as session:
            service = await session.get(Service, service_id)
            if not service:
                return None
            for key, value in data.items():
                if hasattr(service, key) and value is not None:
                    setattr(service, key, value)
            await session.commit()
            await session.refresh(service)
            return service
    
    @staticmethod
    async def delete_service(service_id: int) -> bool:
        async with async_session_maker() as session:
            service = await session.get(Service, service_id)
            if not service:
                return False
            await session.delete(service)
            await session.commit()
            return True
    
    @staticmethod
    async def purchase_service(telegram_id: int, service_id: int, quantity: int = 1) -> Optional[Order]:
        service = await ServiceCatalogService.get_service_by_id(service_id)
        if not service or not service.is_active or not service.is_in_stock():
            return None
        
        total_price = service.price * quantity
        wallet_available = (await WalletService.get_balance(telegram_id))["available"]
        
        if wallet_available < total_price:
            return None
        
        # Generate order number
        order_number = f"ORD-{random.randint(100000, 999999)}"
        
        async with async_session_maker() as session:
            order = Order(
                order_number=order_number,
                user_id=telegram_id,
                service_id=service_id,
                quantity=quantity,
                unit_price=service.price,
                total_price=total_price,
                period=service.period.value,
                status=OrderStatus.PENDING
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
        
        # Hold balance
        held = await WalletService.hold_balance(telegram_id, total_price, order.id)
        if not held:
            return None
        
        # Complete purchase if auto delivery
        if service.delivery_type == "auto":
            order = await ServiceCatalogService.deliver_service(order.id)
        else:
            # Manual delivery - notify admin
            from app.services.notification_service import NotificationService
            await NotificationService.notify_admins(f"New order #{order_number} requires manual delivery")
        
        return order
    
    @staticmethod
    async def deliver_service(order_id: int) -> Optional[Order]:
        async with async_session_maker() as session:
            order = await session.get(Order, order_id)
            if not order or order.status != OrderStatus.PENDING:
                return None
            
            service = await session.get(Service, order.service_id)
            if not service:
                return None
            
            # Release hold and complete purchase
            success = await WalletService.release_hold(order.user_id, order.total_price, order.id, complete_purchase=True)
            if not success:
                return None
            
            order.status = OrderStatus.COMPLETED
            order.delivered_at = func.now()
            
            # Generate delivery data based on service type
            if service.type == ServiceType.VPN:
                # Generate VPN credentials
                username = f"user_{order.user_id}_{order.id}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                order.delivery_data = {
                    "username": username,
                    "password": password,
                    "server": service.location,
                    "config_url": f"https://vpn.teos.local/config/{username}"
                }
            elif service.type == ServiceType.ACCOUNT:
                order.delivery_data = {
                    "account": f"account_{order.user_id}",
                    "valid_until": (func.now() + 365*24*3600)
                }
            else:
                order.delivery_data = {"note": "Service delivered. Contact support for details."}
            
            # Reduce stock
            service.reduce_stock(order.quantity)
            
            await session.commit()
            await session.refresh(order)
            
            # Send notification to user
            from app.services.notification_service import NotificationService
            await NotificationService.notify_user(order.user_id, f"✅ Order #{order.order_number} completed! Delivery info: {order.delivery_data}")
            
            return order
