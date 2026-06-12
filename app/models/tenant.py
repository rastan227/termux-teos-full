from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import json

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Bot configuration
    bot_token = Column(String(255), nullable=True)
    bot_username = Column(String(64), nullable=True)
    webhook_url = Column(String(255), nullable=True)
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#0088cc")
    secondary_color = Column(String(7), default="#00aaff")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    settings = Column(JSON, nullable=True)  # tenant-specific settings
    theme = Column(JSON, nullable=True)  # theme overrides
    
    # Ownership
    owner_id = Column(BigInteger, nullable=False, index=True)  # telegram_id of tenant owner
    
    # Limits
    max_users = Column(Integer, default=10000)
    max_storage_gb = Column(Integer, default=100)
    max_monthly_bandwidth_gb = Column(Integer, default=1000)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    
    def get_setting(self, key: str, default=None):
        if self.settings:
            return self.settings.get(key, default)
        return default
    
    def set_setting(self, key: str, value):
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "bot_username": self.bot_username,
            "logo_url": self.logo_url,
            "primary_color": self.primary_color,
            "is_active": self.is_active,
            "is_trial": self.is_trial,
            "trial_ends_at": self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            "max_users": self.max_users,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
