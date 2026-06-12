from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def is_expired(self) -> bool:
        return func.now() > self.expires_at
    
    def extend(self, seconds: int = 86400):
        from datetime import datetime, timedelta
        self.expires_at = datetime.utcnow() + timedelta(seconds=seconds)
