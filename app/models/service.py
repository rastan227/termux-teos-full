from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, BigInteger, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ServiceType(str, enum.Enum):
    VPN = "vpn"
    SERVER = "server"
    ACCOUNT = "account"
    CREDIT = "credit"
    OTHER = "other"

class ServicePeriod(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    ONE_TIME = "one_time"

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(ServiceType), default=ServiceType.OTHER)
    category = Column(String(50), index=True)
    
    # Pricing
    price = Column(Integer, nullable=False)  # in smallest unit
    compare_price = Column(Integer, nullable=True)  # old price for discount display
    period = Column(Enum(ServicePeriod), default=ServicePeriod.MONTHLY)
    setup_fee = Column(Integer, default=0)
    
    # Specifications
    spec_data = Column(JSON, nullable=True)  # e.g., {"bandwidth": "100GB", "speed": "10Gbps"}
    location = Column(String(100), nullable=True)
    stock = Column(Integer, default=-1)  # -1 = unlimited
    
    # Delivery
    delivery_type = Column(String(20), default="auto")  # auto, manual, api
    delivery_webhook = Column(String(255), nullable=True)
    delivery_data = Column(JSON, nullable=True)
    
    # Limits
    max_per_user = Column(Integer, default=1)
    trial_available = Column(Boolean, default=False)
    trial_days = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # Metadata
    image_url = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="service")
    
    def is_in_stock(self) -> bool:
        return self.stock == -1 or self.stock > 0
    
    def reduce_stock(self, quantity: int = 1) -> bool:
        if self.stock == -1:
            return True
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def get_final_price(self) -> int:
        return self.price
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "type": self.type.value,
            "price": self.price,
            "compare_price": self.compare_price,
            "period": self.period.value,
            "spec_data": self.spec_data,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
        }
