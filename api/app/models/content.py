from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Content(Base):
    """Модель контента (фильмы, сериалы)"""
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # 'movie' или 'series'
    release_year = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # для фильмов
    total_seasons = Column(Integer, nullable=True)  # для сериалов
    total_episodes = Column(Integer, nullable=True)  # для сериалов
    imdb_rating = Column(Float, nullable=True)
    imdb_id = Column(String(20), unique=True, nullable=True)
    poster_url = Column(String(500), nullable=True)
    genre = Column(String(255), nullable=True)
    director = Column(String(255), nullable=True)
    actors_cast = Column(Text, nullable=True)
    language = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Внешний ключ на категорию
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Технические поля
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Связи
    category = relationship("Category")
    view_history = relationship("ViewHistory")
    watchlists = relationship("Watchlist")

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"