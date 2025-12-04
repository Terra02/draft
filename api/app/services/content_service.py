from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List, Dict, Any
import logging

from app.models.content import Content
from app.schemas.content import ContentCreate, ContentUpdate
from app.services.imdb_service import IMDbService

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.imdb_service = IMDbService()

    async def get_content_by_id(self, content_id: int) -> Optional[Content]:
        """Получить контент по ID"""
        result = await self.db.execute(
            select(Content).where(Content.id == content_id)
        )
        return result.scalar_one_or_none()

    async def get_content_by_imdb_id(self, imdb_id: str) -> Optional[Content]:
        """Получить контент по IMDb ID"""
        result = await self.db.execute(
            select(Content).where(Content.imdb_id == imdb_id)
        )
        return result.scalar_one_or_none()

    async def create_content(self, content_data: ContentCreate) -> Content:
        """Создать новый контент"""
        # Проверяем, существует ли контент с таким IMDb ID
        if content_data.imdb_id:
            existing_content = await self.get_content_by_imdb_id(content_data.imdb_id)
            if existing_content:
                return existing_content

        content = Content(**content_data.model_dump())
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        logger.info(f"Created new content: {content.title}")
        return content

    async def search_content(
        self, 
        query: str, 
        content_type: Optional[str] = None,
        category_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """Поиск контента с проверкой в БД и внешнем API"""
        # Сначала ищем в базе данных
        db_results = await self._search_in_database(query, content_type, category_id, skip, limit)
        
        if db_results["total"] > 0:
            logger.info(f"Found {db_results['total']} results in database for query: {query}")
            return db_results
        
        # Если в базе нет результатов, ищем во внешнем API
        logger.info(f"No results in database for query: {query}, searching external API")
        external_results = await self._search_in_external_api(query, content_type)
        
        if external_results:
            # Сохраняем найденные результаты в базу
            saved_results = await self._save_external_results(external_results)
            return await self._search_in_database(query, content_type, category_id, skip, limit)
        
        return {"results": [], "total": 0, "page": skip // limit + 1, "size": limit}

    async def _search_in_database(
        self,
        query: str,
        content_type: Optional[str] = None,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Поиск контента в базе данных"""
        stmt = select(Content).where(
            or_(
                Content.title.ilike(f"%{query}%"),
                Content.original_title.ilike(f"%{query}%"),
                Content.description.ilike(f"%{query}%")
            )
        )

        if content_type:
            stmt = stmt.where(Content.content_type == content_type)

        if category_id:
            stmt = stmt.where(Content.category_id == category_id)

        # Получаем общее количество
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()

        # Получаем результаты
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        content_list = result.scalars().all()

        return {
            "results": content_list,
            "total": total,
            "page": skip // limit + 1,
            "size": limit
        }

    async def _search_in_external_api(
        self, 
        query: str, 
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Поиск контента во внешнем API (OMDb)"""
        try:
            external_results = []
            
            # Ищем фильмы
            if not content_type or content_type == 'movie':
                movie_data = await self.imdb_service.search_content(query, 'movie')
                if movie_data:
                    external_results.append(movie_data)
            
            # Ищем сериалы
            if not content_type or content_type == 'series':
                series_data = await self.imdb_service.search_content(query, 'series')
                if series_data:
                    external_results.append(series_data)
            
            return external_results
        except Exception as e:
            logger.error(f"Error searching external API: {e}")
            return []

    async def _save_external_results(self, external_results: List[Dict[str, Any]]) -> List[Content]:
        """Сохранить результаты из внешнего API в базу данных"""
        saved_contents = []
        
        for external_data in external_results:
            try:
                # Проверяем, существует ли уже контент с таким IMDb ID
                if external_data.get('imdb_id'):
                    existing_content = await self.get_content_by_imdb_id(external_data['imdb_id'])
                    if existing_content:
                        saved_contents.append(existing_content)
                        continue

                # Создаем объект контента
                content_data = ContentCreate(**external_data)
                content = await self.create_content(content_data)
                saved_contents.append(content)
                logger.info(f"Saved external content to database: {content.title}")
                
            except Exception as e:
                logger.error(f"Error saving external content {external_data.get('title')}: {e}")
                continue
        
        return saved_contents

    async def update_content(self, content_id: int, content_data: ContentUpdate) -> Optional[Content]:
        """Обновить данные контента"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return None

        update_data = content_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)

        await self.db.commit()
        await self.db.refresh(content)
        logger.info(f"Updated content: {content.title}")
        return content

    async def delete_content(self, content_id: int) -> bool:
        """Удалить контент"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return False

        await self.db.delete(content)
        await self.db.commit()
        logger.info(f"Deleted content: {content.title}")
        return True

    async def get_content_by_category(self, category_id: int, skip: int = 0, limit: int = 20) -> List[Content]:
        """Получить контент по категории"""
        result = await self.db.execute(
            select(Content)
            .where(Content.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_content(self, limit: int = 10) -> List[Content]:
        """Получить недавно добавленный контент"""
        result = await self.db.execute(
            select(Content)
            .order_by(Content.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_popular_content(self, limit: int = 10) -> List[Content]:
        """Получить популярный контент (по рейтингу)"""
        result = await self.db.execute(
            select(Content)
            .where(Content.imdb_rating.isnot(None))
            .order_by(Content.imdb_rating.desc())
            .limit(limit)
        )
        return result.scalars().all()