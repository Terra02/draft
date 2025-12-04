from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def get_pagination_info(total: int, page: int, size: int) -> dict:
    """Получить информацию о пагинации"""
    pages = (total + size - 1) // size
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }