from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import secrets

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"

class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"
    PARTIAL = "partial"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    discount = Column(Integer, default=0)
    final_price = Column(Integer, nullable=False)
    
    period = Column(String(20), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    
    # Delivery
    delivery_data = Column(JSON, nullable=True)
    delivery_notes = Column(Text, nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    delivery_attempts = Column(Integer, default=0)
    
    # Payment
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_gateway = Column(String(50), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service")
    transaction = relationship("Transaction", back_populates="order")
    
    @staticmethod
    def generate_order_number() -> str:
        timestamp = func.now().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"ORD-{timestamp}-{random_part}"
    
    def mark_paid(self, transaction_id: int, gateway: str = None) -> None:
        self.status = OrderStatus.PAID
        self.payment_status = PaymentStatus.PAID
        self.transaction_id = transaction_id
        self.payment_gateway = gateway
    
    def mark_processing(self) -> None:
        self.status = OrderStatus.PROCESSING
    
    def mark_completed(self, delivery_data: dict = None) -> None:
        self.status = OrderStatus.COMPLETED
        self.completed_at = func.now()
        if delivery_data:
            self.delivery_data = delivery_data
    
    def mark_cancelled(self, reason: str = None) -> None:
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = func.now()
        if reason:
            self.notes = reason
    
    def mark_expired(self) -> None:
        self.status = OrderStatus.EXPIRED
    
    def is_paid(self) -> bool:
        return self.payment_status == PaymentStatus.PAID
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "user_id": self.user_id,
            "service_id": self.service_id,
            "quantity": self.quantity,
            "final_price": self.final_price,
            "status": self.status.value,
            "payment_status": self.payment_status.value,
            "delivery_data": self.delivery_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
