from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, JSON, Float
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class MemoryType(str, enum.Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"
    USER_PREFERENCE = "user_preference"
    KNOWLEDGE = "knowledge"

class AIMemory(Base):
    __tablename__ = "ai_memories"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    memory_type = Column(String(20), default=MemoryType.SHORT_TERM.value)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="ai_memories")
    
    @classmethod
    def create_short_term(cls, user_id: int, key: str, value: str, ttl_seconds: int = 3600):
        expires_at = func.now() + ttl_seconds
        return cls(
            user_id=user_id,
            memory_type=MemoryType.SHORT_TERM.value,
            key=key,
            value=value,
            expires_at=expires_at
        )
    
    @classmethod
    def create_long_term(cls, user_id: int, key: str, value: str):
        return cls(
            user_id=user_id,
            memory_type=MemoryType.LONG_TERM.value,
            key=key,
            value=value
        )

class AIInteraction(Base):
    __tablename__ = "ai_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    feedback_score = Column(Integer, nullable=True)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ai_interactions")
