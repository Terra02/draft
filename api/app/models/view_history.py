from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ViewHistory(Base):
    __tablename__ = "view_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # View details
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Float, nullable=True)  # 1-10
    season = Column(Integer, nullable=True)  # для сериалов
    episode = Column(Integer, nullable=True)  # для сериалов
    episode_title = Column(String, nullable=True)  # для сериалов
    duration_watched = Column(Integer, nullable=True)  # в минутах
    rewatch = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    content = relationship("Content")
    
    def __repr__(self):
        return f"<ViewHistory(id={self.id}, user_id={self.user_id}, content_id={self.content_id})>"