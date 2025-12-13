from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


def _validate_watched_at(value: Optional[datetime]) -> Optional[datetime]:
    """Validate watched_at is not in the future and not beyond 2024."""

    if value is None:
        return value

    max_allowed_date = date(2024, 12, 31)
    if value.date() > max_allowed_date:
        raise ValueError("Дата просмотра не может быть позже 31.12.2024.")

    now = datetime.now(tz=value.tzinfo) if value.tzinfo else datetime.now()
    if value > now:
        raise ValueError("Дата просмотра не может быть в будущем.")

    return value


class ViewHistoryBase(BaseModel):
    user_id: int
    content_id: int
    watched_at: Optional[datetime] = None
    rating: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    duration_watched: Optional[int] = None
    rewatch: bool = False
    notes: Optional[str] = None

    @field_validator("watched_at")
    @classmethod
    def validate_watched_at(cls, value: Optional[datetime]) -> Optional[datetime]:
        return _validate_watched_at(value)


class ViewHistoryCreate(ViewHistoryBase):
    pass


class ViewHistoryUpdate(BaseModel):
    watched_at: Optional[datetime] = None
    rating: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    duration_watched: Optional[int] = None
    rewatch: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("watched_at")
    @classmethod
    def validate_watched_at(cls, value: Optional[datetime]) -> Optional[datetime]:
        return _validate_watched_at(value)


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
