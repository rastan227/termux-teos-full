from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base

class SystemHealth(Base):
    __tablename__ = "system_health"
    
    id = Column(Integer, primary_key=True)
    component = Column(String(50), nullable=False)  # bot, api, database, redis
    status = Column(String(20), default="healthy")  # healthy, degraded, down
    latency_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @classmethod
    def record_health(cls, component: str, status: str, latency_ms: float = None, error: str = None):
        return cls(
            component=component,
            status=status,
            latency_ms=latency_ms,
            error_message=error
        )
