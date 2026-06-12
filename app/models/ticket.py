from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(64), unique=True)
    description = Column(Text, nullable=True)
    assign_to_role = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=True)
    
    subject = Column(String(200), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    
    assigned_to = Column(BigInteger, nullable=True)  # admin telegram_id
    closed_by = Column(BigInteger, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    meta_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    
    def close(self, closed_by_id: int) -> None:
        self.status = TicketStatus.CLOSED
        self.closed_by = closed_by_id
        self.closed_at = func.now()
    
    def reopen(self) -> None:
        self.status = TicketStatus.OPEN
        self.closed_by = None
        self.closed_at = None
    
    def assign(self, admin_id: int) -> None:
        self.assigned_to = admin_id
        self.status = TicketStatus.IN_PROGRESS

class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    message = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    attachments = Column(JSON, nullable=True)  # list of file URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    ticket = relationship("Ticket", back_populates="messages")
    user = relationship("User", back_populates="ticket_messages")
