from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Integer, Enum, ForeignKey, Text, JSON, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.security import hash_password, verify_password
import enum
import json
from typing import List, Optional, Set

class UserRole(str, enum.Enum):
    USER = "user"
    MUSIC_ADMIN = "music_admin"
    SERVICE_ADMIN = "service_admin"
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    
class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_user_telegram_id", "telegram_id"),
        Index("idx_user_role_status", "role", "status"),
    )
    
    # Primary
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    
    # Personal info
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(128), nullable=True)
    language = Column(String(5), default="fa")
    
    # Role & permissions
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)
    permissions_override = Column(Text, nullable=True)  # JSON list of extra permissions
    custom_commands = Column(Text, nullable=True)  # JSON for custom menu
    
    # Status
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(String(255), nullable=True)
    banned_at = Column(DateTime(timezone=True), nullable=True)
    banned_by = Column(BigInteger, nullable=True)
    
    # Wallet
    wallet_balance = Column(Integer, default=0, nullable=False)  # in smallest unit (IRR * 10)
    wallet_hold = Column(Integer, default=0, nullable=False)  # reserved for pending orders
    total_spent = Column(Integer, default=0, nullable=False)
    total_deposits = Column(Integer, default=0, nullable=False)
    
    # Stats
    total_downloads = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    total_tickets = Column(Integer, default=0)
    total_referrals = Column(Integer, default=0)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # Referral
    referrer_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    referral_code = Column(String(32), unique=True, nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Integer, default=0)
    
    # AI & personalization
    ai_preferences = Column(JSON, nullable=True)  # stored as JSON
    favorite_genres = Column(JSON, nullable=True)  # list of strings
    favorite_artists = Column(JSON, nullable=True)
    behavior_profile = Column(JSON, nullable=True)  # user behavior score
    last_ai_interaction = Column(DateTime(timezone=True), nullable=True)
    
    # Security
    login_attempts = Column(Integer, default=0)
    last_login_ip = Column(String(45), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    session_token = Column(String(255), nullable=True)
    session_expires_at = Column(DateTime(timezone=True), nullable=True)
    totp_secret = Column(String(32), nullable=True)  # 2FA
    is_2fa_enabled = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    ticket_messages = relationship("TicketMessage", back_populates="user")
    music_likes = relationship("MusicLike", back_populates="user", cascade="all, delete-orphan")
    music_plays = relationship("MusicPlay", back_populates="user", cascade="all, delete-orphan")
    music_reports = relationship("MusicReport", back_populates="reporter")
    payment_requests = relationship("PaymentRequest", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    ai_memories = relationship("AIMemory", back_populates="user", cascade="all, delete-orphan")
    ai_interactions = relationship("AIInteraction", back_populates="user", cascade="all, delete-orphan")
    
    def get_permissions(self) -> Set[str]:
        """Get all permissions for this user based on role and overrides"""
        base_perms = {
            UserRole.USER: {"view_music", "download_music", "view_services", "view_wallet", "create_ticket", "view_profile"},
            UserRole.MUSIC_ADMIN: {"view_music", "download_music", "upload_music", "edit_music", "delete_music", "view_music_stats", "moderate_music"},
            UserRole.SERVICE_ADMIN: {"view_services", "create_service", "edit_service", "delete_service", "view_orders", "approve_payment", "manage_orders"},
            UserRole.SUPER_ADMIN: {"*", "manage_users", "manage_tenants", "view_all_logs"},
            UserRole.OWNER: {"*", "manage_system", "manage_plugins", "manage_backup", "manage_updates"}
        }.get(self.role, {"view_music", "view_services"})
        
        if self.permissions_override:
            try:
                extra = set(json.loads(self.permissions_override))
                base_perms.update(extra)
            except:
                pass
        return base_perms
    
    def has_permission(self, perm: str) -> bool:
        perms = self.get_permissions()
        return "*" in perms or perm in perms
    
    def is_admin(self) -> bool:
        return self.role in [UserRole.MUSIC_ADMIN, UserRole.SERVICE_ADMIN, UserRole.SUPER_ADMIN, UserRole.OWNER]
    
    def is_owner(self) -> bool:
        return self.role == UserRole.OWNER
    
    def can_manage_tenant(self) -> bool:
        return self.role in [UserRole.SUPER_ADMIN, UserRole.OWNER]
    
    def get_wallet_available(self) -> int:
        return self.wallet_balance - self.wallet_hold
    
    def add_balance(self, amount: int, commit_callback=None) -> bool:
        if amount <= 0:
            return False
        self.wallet_balance += amount
        self.total_deposits += amount
        if commit_callback:
            commit_callback()
        return True
    
    def deduct_balance(self, amount: int, commit_callback=None) -> bool:
        if amount <= 0 or self.get_wallet_available() < amount:
            return False
        self.wallet_balance -= amount
        self.total_spent += amount
        if commit_callback:
            commit_callback()
        return True
    
    def hold_balance(self, amount: int) -> bool:
        if self.get_wallet_available() < amount:
            return False
        self.wallet_hold += amount
        return True
    
    def release_hold(self, amount: int) -> None:
        self.wallet_hold = max(0, self.wallet_hold - amount)
    
    def increment_login_attempts(self) -> int:
        self.login_attempts += 1
        return self.login_attempts
    
    def reset_login_attempts(self) -> None:
        self.login_attempts = 0
    
    def update_last_seen(self) -> None:
        self.last_seen = func.now()
    
    def ban(self, reason: str, banned_by_id: int) -> None:
        self.is_banned = True
        self.status = UserStatus.BANNED
        self.ban_reason = reason
        self.banned_by = banned_by_id
        self.banned_at = func.now()
    
    def unban(self) -> None:
        self.is_banned = False
        self.status = UserStatus.ACTIVE
        self.ban_reason = None
        self.banned_by = None
        self.banned_at = None
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "status": self.status.value,
            "wallet_balance": self.wallet_balance,
            "wallet_available": self.get_wallet_available(),
            "total_spent": self.total_spent,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }
        if include_sensitive:
            data.update({
                "phone": self.phone,
                "email": self.email,
                "referral_code": self.referral_code,
                "referral_count": self.referral_count,
                "referral_earnings": self.referral_earnings,
            })
        return data
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, role={self.role})>"
