import logging
import json
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.wallet_service import WalletService
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.core.database import async_session_maker
import aiohttp
import uuid

logger = logging.getLogger(__name__)

class PaymentService:
    
    @staticmethod
    async def create_payment_request(user_id: int, amount: int, method: str, metadata: dict = None) -> Dict:
        """Create a payment request (mock or real gateway)"""
        if settings.PAYMENT_MOCK:
            return {
                "id": str(uuid.uuid4()),
                "amount": amount,
                "method": method,
                "status": "pending",
                "instructions": "لطفاً رسید را از طریق ربات ارسال کنید."
            }
        else:
            # Integration with Zarinpal, Stripe, etc.
            gateway_url = f"{settings.PAYMENT_GATEWAY_URL}/api/v1/payment"
            payload = {
                "amount": amount,
                "callback_url": settings.PAYMENT_CALLBACK_URL,
                "metadata": metadata or {}
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(gateway_url, json=payload) as resp:
                    data = await resp.json()
                    return data
    
    @staticmethod
    async def verify_payment(transaction_id: str, gateway: str) -> bool:
        """Verify payment with gateway"""
        # Mock verification
        return True
    
    @staticmethod
    async def process_payment_callback(gateway_data: dict) -> Optional[Transaction]:
        """Handle payment gateway callback"""
        # Extract data
        order_id = gateway_data.get("order_id")
        amount = gateway_data.get("amount")
        user_id = gateway_data.get("user_id")
        gateway_tx_id = gateway_data.get("transaction_id")
        
        # Create transaction record
        async with async_session_maker() as session:
            tx = Transaction(
                transaction_hash=str(uuid.uuid4()),
                user_id=user_id,
                amount=amount,
                balance_before=0,  # Will be updated
                balance_after=0,
                type=TransactionType.DEPOSIT,
                status=TransactionStatus.PENDING,
                description=f"Payment via {gateway}",
                gateway=gateway,
                gateway_transaction_id=gateway_tx_id
            )
            session.add(tx)
            await session.commit()
            await session.refresh(tx)
            
            # Add to wallet
            await WalletService.add_balance(user_id, amount, f"Gateway payment {gateway_tx_id}", str(tx.id))
            tx.mark_completed()
            await session.commit()
            return tx
