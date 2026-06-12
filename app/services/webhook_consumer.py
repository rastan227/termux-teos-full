import logging
import json
import hashlib
import hmac
from fastapi import Request, HTTPException
from app.services.wallet_service import WalletService
from app.services.order_service import OrderService
from app.services.notification_engine import NotificationEngine, Notification, NotificationChannel, NotificationPriority
from app.core.config import settings

logger = logging.getLogger(__name__)

class WebhookConsumer:
    
    @staticmethod
    async def process_payment_gateway(request: Request, gateway: str) -> dict:
        """Process incoming webhook from payment gateway"""
        body = await request.body()
        signature = request.headers.get("X-Signature", "")
        
        # Verify signature
        if not WebhookConsumer._verify_signature(body, signature, gateway):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        data = json.loads(body)
        
        if gateway == "zarinpal":
            return await WebhookConsumer._handle_zarinpal(data)
        elif gateway == "stripe":
            return await WebhookConsumer._handle_stripe(data)
        elif gateway == "mock":
            return await WebhookConsumer._handle_mock(data)
        else:
            logger.warning(f"Unknown gateway: {gateway}")
            return {"status": "ignored"}
    
    @staticmethod
    async def _handle_zarinpal(data: dict) -> dict:
        authority = data.get("Authority")
        status = data.get("Status")
        if status == "OK":
            # Verify with Zarinpal API
            # For now, assume success
            user_id = data.get("user_id")
            amount = data.get("amount")
            if user_id and amount:
                await WalletService.add_balance(int(user_id), int(amount), f"Zarinpal payment {authority}")
                return {"status": "success"}
        return {"status": "failed"}
    
    @staticmethod
    async def _handle_stripe(data: dict) -> dict:
        event_type = data.get("type")
        if event_type == "checkout.session.completed":
            session_data = data["data"]["object"]
            user_id = session_data.get("client_reference_id")
            amount = session_data.get("amount_total", 0) // 10  # to IRR
            if user_id and amount:
                await WalletService.add_balance(int(user_id), int(amount), f"Stripe payment {session_data['id']}")
                return {"status": "success"}
        return {"status": "ignored"}
    
    @staticmethod
    async def _handle_mock(data: dict) -> dict:
        user_id = data.get("user_id")
        amount = data.get("amount")
        if user_id and amount:
            await WalletService.add_balance(int(user_id), int(amount), "Mock payment")
            return {"status": "success"}
        return {"status": "failed"}
    
    @staticmethod
    def _verify_signature(body: bytes, signature: str, gateway: str) -> bool:
        if gateway == "mock":
            return True
        secret = settings.PAYMENT_WEBHOOK_SECRET
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    async def process_external_service(data: dict, service_type: str) -> dict:
        """Handle webhook from external service (e.g., VPN provider)"""
        logger.info(f"External webhook from {service_type}: {data}")
        if service_type == "vpn_delivery":
            order_id = data.get("order_id")
            credentials = data.get("credentials")
            if order_id:
                # Update order with credentials
                from app.services.order_service import OrderService
                await OrderService.update_delivery_data(order_id, credentials)
                # Notify user
                user_id = data.get("user_id")
                if user_id:
                    await NotificationEngine.send(Notification(
                        user_id=user_id,
                        title="VPN فعال شد",
                        message="سرویس VPN شما با موفقیت فعال شد. اطلاعات ارسال شد.",
                        channel=NotificationChannel.TELEGRAM,
                        priority=NotificationPriority.HIGH
                    ))
                return {"status": "received"}
        return {"status": "ignored"}
