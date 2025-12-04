from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.content import ContentResponse, ContentCreate, ContentUpdate, ContentSearchResponse
from app.services.content_service import ContentService

router = APIRouter(prefix="/content", tags=["content"])

@router.get("/search", response_model=ContentSearchResponse)
async def search_content(
    query: str = Query(..., min_length=1, description="Search query for content"),
    content_type: Optional[str] = Query(None, regex="^(movie|series)$", description="Filter by content type"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for content in database and external APIs.
    
    First searches in the local database. If no results found,
    searches in external APIs (OMDb) and saves results to database.
    """
    content_service = ContentService(db)
    result = await content_service.search_content(query, content_type, category_id, skip, limit)
    return result

@router.get("/", response_model=ContentSearchResponse)
async def get_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None, regex="^(movie|series)$"),
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get content list with optional filtering"""
    content_service = ContentService(db)
    
    # Используем поиск с пустым запросом для получения всего контента
    result = await content_service.search_content("", content_type, category_id, skip, limit)
    return result

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(content_id: int, db: AsyncSession = Depends(get_db)):
    """Get content by ID"""
    content_service = ContentService(db)
    content = await content_service.get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content

@router.get("/imdb/{imdb_id}", response_model=ContentResponse)
async def get_content_by_imdb_id(imdb_id: str, db: AsyncSession = Depends(get_db)):
    """Get content by IMDb ID"""
    content_service = ContentService(db)
    content = await content_service.get_content_by_imdb_id(imdb_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content

@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(content_data: ContentCreate, db: AsyncSession = Depends(get_db)):
    """Create new content"""
    content_service = ContentService(db)
    content = await content_service.create_content(content_data)
    return content

@router.post("/from-imdb/{imdb_id}", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_from_imdb(imdb_id: str, db: AsyncSession = Depends(get_db)):
    """Create content from IMDb ID"""
    content_service = ContentService(db)
    imdb_service = content_service.imdb_service
    
    # Получаем данные из OMDb
    imdb_data = await imdb_service.get_content_by_imdb_id(imdb_id)
    if not imdb_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found in IMDb"
        )
    
    # Создаем контент в базе
    content_data = ContentCreate(**imdb_data)
    content = await content_service.create_content(content_data)
    return content

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int, 
    content_data: ContentUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update content"""
    content_service = ContentService(db)
    content = await content_service.update_content(content_id, content_data)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    """Delete content"""
    content_service = ContentService(db)
    success = await content_service.delete_content(content_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )