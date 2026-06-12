from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
