from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ViewHistoryBase(BaseModel):
    user_id: int
    content_id: int
    rating: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    duration_watched: Optional[int] = None
    rewatch: bool = False
    notes: Optional[str] = None

class ViewHistoryCreate(ViewHistoryBase):
    pass

class ViewHistoryUpdate(BaseModel):
    rating: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    duration_watched: Optional[int] = None
    rewatch: Optional[bool] = None
    notes: Optional[str] = None

class ViewHistoryInDB(ViewHistoryBase):
    id: int
    watched_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ViewHistoryResponse(ViewHistoryInDB):
    content_title: Optional[str] = None
    content_type: Optional[str] = None

class ViewHistoryWithContent(ViewHistoryResponse):
    content: Optional[dict] = None