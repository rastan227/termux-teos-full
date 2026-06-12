from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import secrets

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PURCHASE = "purchase"
    REFUND = "refund"
    REFERRAL_BONUS = "referral_bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    SERVICE_FEE = "service_fee"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String(64), unique=True, default=lambda: secrets.token_hex(32), index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    amount = Column(Integer, nullable=False)  # can be positive or negative
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    description = Column(String(255), nullable=True)
    reference = Column(String(128), nullable=True)  # payment reference, gateway tx id
    meta_data = Column(JSON, nullable=True)
    
    # Gateway info
    gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(128), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    order = relationship("Order", back_populates="transaction")
    
    def mark_completed(self) -> None:
        self.status = TransactionStatus.COMPLETED
        self.completed_at = func.now()
    
    def mark_failed(self, reason: str = None) -> None:
        self.status = TransactionStatus.FAILED
        if reason:
            self.description = reason
    
    def mark_reversed(self) -> None:
        self.status = TransactionStatus.REVERSED
    
    def is_deposit(self) -> bool:
        return self.type == TransactionType.DEPOSIT
    
    def is_withdrawal(self) -> bool:
        return self.type == TransactionType.WITHDRAWAL
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hash": self.transaction_hash,
            "amount": self.amount,
            "type": self.type.value,
            "status": self.status.value,
            "description": self.description,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
