import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.order import Order, OrderStatus
from app.core.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class WalletService:
    
    @staticmethod
    async def get_balance(telegram_id: int) -> Dict[str, int]:
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user:
                return {"balance": 0, "hold": 0, "available": 0}
            return {
                "balance": user.wallet_balance,
                "hold": user.wallet_hold,
                "available": user.get_wallet_available()
            }
    
    @staticmethod
    async def add_balance(telegram_id: int, amount: int, description: str, 
                          reference: Optional[str] = None, tx_type: TransactionType = TransactionType.DEPOSIT) -> bool:
        if amount <= 0:
            return False
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user:
                return False
            
            old_balance = user.wallet_balance
            user.add_balance(amount)
            
            tx = Transaction(
                user_id=telegram_id,
                amount=amount,
                balance_before=old_balance,
                balance_after=user.wallet_balance,
                type=tx_type,
                status=TransactionStatus.COMPLETED,
                description=description,
                reference=reference
            )
            session.add(tx)
            await session.commit()
            logger.info(f"Added {amount} to wallet of {telegram_id}: {description}")
            return True
    
    @staticmethod
    async def deduct_balance(telegram_id: int, amount: int, description: str, 
                             reference: Optional[str] = None) -> bool:
        if amount <= 0:
            return False
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user or user.get_wallet_available() < amount:
                return False
            
            old_balance = user.wallet_balance
            if not user.deduct_balance(amount):
                return False
            
            tx = Transaction(
                user_id=telegram_id,
                amount=-amount,
                balance_before=old_balance,
                balance_after=user.wallet_balance,
                type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.COMPLETED,
                description=description,
                reference=reference
            )
            session.add(tx)
            await session.commit()
            return True
    
    @staticmethod
    async def hold_balance(telegram_id: int, amount: int, order_id: int) -> bool:
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user or user.get_wallet_available() < amount:
                return False
            user.hold_balance(amount)
            # Store hold info in order meta
            order = await session.get(Order, order_id)
            if order:
                if not order.meta_data:
                    order.meta_data = {}
                order.meta_data["held_amount"] = amount
            await session.commit()
            return True
    
    @staticmethod
    async def release_hold(telegram_id: int, amount: int, order_id: int, complete_purchase: bool = False) -> bool:
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user:
                return False
            user.release_hold(amount)
            
            order = await session.get(Order, order_id)
            if order and complete_purchase:
                # Actually deduct the held amount
                old_balance = user.wallet_balance
                user.wallet_balance -= amount
                user.total_spent += amount
                tx = Transaction(
                    user_id=telegram_id,
                    amount=-amount,
                    balance_before=old_balance,
                    balance_after=user.wallet_balance,
                    type=TransactionType.PURCHASE,
                    status=TransactionStatus.COMPLETED,
                    description=f"Order #{order.order_number}",
                    reference=str(order_id)
                )
                session.add(tx)
                order.status = OrderStatus.PAID
                order.transaction_id = tx.id
            await session.commit()
            return True
    
    @staticmethod
    async def create_payment_request(telegram_id: int, amount: int, method: str, 
                                      receipt_image: Optional[str] = None) -> Optional[int]:
        from app.models.transaction import PaymentRequest
        async with async_session_maker() as session:
            user = await session.get(User, telegram_id)
            if not user:
                return None
            req = PaymentRequest(
                user_id=telegram_id,
                amount=amount,
                method=method,
                receipt_image=receipt_image,
                status="pending"
            )
            session.add(req)
            await session.commit()
            await session.refresh(req)
            return req.id
    
    @staticmethod
    async def get_payment_requests(status: str = "pending", limit: int = 100) -> List[Dict]:
        from app.models.transaction import PaymentRequest
        async with async_session_maker() as session:
            stmt = select(PaymentRequest).where(PaymentRequest.status == status).limit(limit)
            result = await session.execute(stmt)
            reqs = result.scalars().all()
            return [{
                "id": r.id,
                "user_id": r.user_id,
                "amount": r.amount,
                "method": r.method,
                "receipt_image": r.receipt_image,
                "created_at": r.created_at.isoformat()
            } for r in reqs]
    
    @staticmethod
    async def approve_payment_request(request_id: int, admin_id: int) -> bool:
        from app.models.transaction import PaymentRequest
        async with async_session_maker() as session:
            req = await session.get(PaymentRequest, request_id)
            if not req or req.status != "pending":
                return False
            req.status = "approved"
            req.approved_by = admin_id
            req.approved_at = datetime.utcnow()
            
            # Add balance
            success = await WalletService.add_balance(
                req.user_id, req.amount, 
                f"Payment request #{request_id} approved",
                reference=str(request_id)
            )
            await session.commit()
            return success
    
    @staticmethod
    async def reject_payment_request(request_id: int, admin_id: int, reason: str) -> bool:
        from app.models.transaction import PaymentRequest
        async with async_session_maker() as session:
            req = await session.get(PaymentRequest, request_id)
            if not req or req.status != "pending":
                return False
            req.status = "rejected"
            req.rejection_reason = reason
            req.approved_by = admin_id
            req.approved_at = datetime.utcnow()
            await session.commit()
            return True
    
    @staticmethod
    async def get_transactions(telegram_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        async with async_session_maker() as session:
            stmt = select(Transaction).where(Transaction.user_id == telegram_id)\
                .order_by(Transaction.created_at.desc()).offset(offset).limit(limit)
            result = await session.execute(stmt)
            txs = result.scalars().all()
            return [tx.to_dict() for tx in txs]
