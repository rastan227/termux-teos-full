import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    
    @staticmethod
    async def send_email(to: str, subject: str, body: str, html: bool = False):
        if not settings.SMTP_HOST:
            logger.warning("SMTP not configured, skipping email")
            return False
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to
            msg["Subject"] = subject
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"Email failed: {e}")
            return False
    
    @staticmethod
    async def send_welcome_email(user_email: str, name: str):
        subject = "خوش آمدید به TEOS"
        body = f"سلام {name}\n\nبه TEOS خوش آمدید. لطفاً برای فعالسازی حساب خود روی لینک زیر کلیک کنید:\n{settings.FRONTEND_URL}/verify"
        await EmailService.send_email(user_email, subject, body)
