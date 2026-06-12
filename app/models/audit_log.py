from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import json

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")
    
    @classmethod
    def create(cls, user_id: int, action: str, **kwargs):
        return cls(
            user_id=user_id,
            action=action,
            resource_type=kwargs.get("resource_type"),
            resource_id=str(kwargs.get("resource_id")) if kwargs.get("resource_id") else None,
            old_value=json.dumps(kwargs.get("old_value")) if kwargs.get("old_value") else None,
            new_value=json.dumps(kwargs.get("new_value")) if kwargs.get("new_value") else None,
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "old_value": json.loads(self.old_value) if self.old_value else None,
            "new_value": json.loads(self.new_value) if self.new_value else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
