import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class SmsService:
    
    @staticmethod
    async def send_sms(phone: str, message: str) -> bool:
        if not settings.SMS_API_KEY:
            logger.warning("SMS API key not configured")
            return False
        try:
            url = f"https://api.kavenegar.com/v1/{settings.SMS_API_KEY}/sms/send.json"
            payload = {
                "receptor": phone,
                "message": message
            }
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"SMS sent to {phone}")
                return True
            else:
                logger.error(f"SMS failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return False
    
    @staticmethod
    async def send_verification_code(phone: str, code: str) -> bool:
        message = f"کد تأیید TEOS: {code}"
        return await SmsService.send_sms(phone, message)
