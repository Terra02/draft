import re
from typing import Optional

def validate_username(username: str) -> bool:
    """Валидация username"""
    if len(username) < 3 or len(username) > 50:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))

def validate_rating(rating: Optional[float]) -> bool:
    """Валидация рейтинга (1-10)"""
    if rating is None:
        return True
    return 1 <= rating <= 10

def validate_content_type(content_type: str) -> bool:
    """Валидация типа контента"""
    return content_type in ['movie', 'series']