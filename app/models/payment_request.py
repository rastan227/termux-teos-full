from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PaymentRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    amount = Column(Integer, nullable=False)
    method = Column(String(50), nullable=False)  # card, online, crypto
    receipt_image = Column(String(500), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    status = Column(Enum(PaymentRequestStatus), default=PaymentRequestStatus.PENDING)
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(BigInteger, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    expired_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="payment_requests")
    
    def approve(self, admin_id: int) -> None:
        self.status = PaymentRequestStatus.APPROVED
        self.approved_by = admin_id
        self.approved_at = func.now()
    
    def reject(self, admin_id: int, reason: str) -> None:
        self.status = PaymentRequestStatus.REJECTED
        self.approved_by = admin_id
        self.rejection_reason = reason
        self.approved_at = func.now()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status.value,
            "receipt_image": self.receipt_image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
