from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Watchlist details
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    priority = Column(Integer, default=1)  # 1-5, где 5 - наивысший приоритет
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")
    content = relationship("Content")
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, user_id={self.user_id}, content_id={self.content_id})>"