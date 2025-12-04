from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WatchlistBase(BaseModel):
    user_id: int
    content_id: int
    priority: int = 1
    notes: Optional[str] = None

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistUpdate(BaseModel):
    priority: Optional[int] = None
    notes: Optional[str] = None

class WatchlistInDB(WatchlistBase):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True

class WatchlistResponse(WatchlistInDB):
    content_title: Optional[str] = None
    content_type: Optional[str] = None

class WatchlistWithContent(WatchlistResponse):
    content: Optional[dict] = None