from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ContentBase(BaseModel):
    title: str
    original_title: Optional[str] = None
    description: Optional[str] = None
    content_type: str  # 'movie' or 'series'
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    total_seasons: Optional[int] = None
    total_episodes: Optional[int] = None
    imdb_rating: Optional[float] = None
    imdb_id: Optional[str] = None
    poster_url: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    category_id: Optional[int] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    total_seasons: Optional[int] = None
    total_episodes: Optional[int] = None
    imdb_rating: Optional[float] = None
    poster_url: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    category_id: Optional[int] = None

class ContentInDB(ContentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContentResponse(ContentInDB):
    pass

class ContentSearchResponse(BaseModel):
    results: List[ContentResponse]
    total: int
    page: int
    size: int