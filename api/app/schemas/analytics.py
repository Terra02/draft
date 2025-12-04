from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

class AnalyticsBase(BaseModel):
    user_id: int
    period_start: datetime
    period_end: datetime

class UserStatsResponse(BaseModel):
    total_movies_watched: int
    total_series_watched: int
    total_hours_watched: float
    average_rating: Optional[float]
    favorite_genre: Optional[str]
    most_watched_director: Optional[str]
    monthly_stats: List[Dict[str, Any]]

class ContentStatsResponse(BaseModel):
    most_watched_movies: List[Dict[str, Any]]
    most_watched_series: List[Dict[str, Any]]
    highest_rated_content: List[Dict[str, Any]]
    recent_additions: List[Dict[str, Any]]

class TimelineStatsResponse(BaseModel):
    daily_stats: List[Dict[str, Any]]
    monthly_stats: List[Dict[str, Any]]
    yearly_stats: List[Dict[str, Any]]