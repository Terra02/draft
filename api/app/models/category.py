from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    """Модель категории для контента"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Связь с контентом (один ко многим)
    contents = relationship("Content")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"