from app.plugins.base_plugin import BasePlugin
from app.services.order_service import OrderService
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

class VPNPlugin(BasePlugin):
    name = "vpn_plugin"
    display_name = "VPN Service Integration"
    version = "1.0.0"
    author = "TEOS Team"
    description = "Provides VPN service delivery via external API"
    
    async def on_install(self):
        logger.info("VPN Plugin installed")
        await self._create_tables()
        return True
    
    async def on_enable(self):
        logger.info("VPN Plugin enabled")
        # Register delivery handler
        from app.services.order_service import OrderService
        # Monkey patch or register callback
        return True
    
    async def on_disable(self):
        logger.info("VPN Plugin disabled")
        return True
    
    async def on_uninstall(self):
        logger.info("VPN Plugin uninstalled")
        await self._drop_tables()
        return True
    
    async def deliver_vpn(self, order_id: int, user_id: int, config: dict) -> bool:
        """Mock VPN delivery - would call real VPN API"""
        # Example: Call external VPN provider API
        logger.info(f"Delivering VPN for order {order_id} to user {user_id}")
        # Return credentials
        credentials = {
            "username": f"teos_{user_id}",
            "password": "generated_password",
            "server": "vpn.teos.local",
            "config_url": "https://vpn.teos.local/config.ovpn"
        }
        await NotificationService.send_to_user(user_id, f"اطلاعات VPN شما:\n{credentials}")
        return True
    
    async def _create_tables(self):
        # Create plugin-specific tables
        pass
    
    async def _drop_tables(self):
        pass
