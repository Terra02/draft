from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List, Dict, Any
import logging

from app.models.content import Content
from app.schemas.content import ContentCreate, ContentUpdate
from app.services.worker_adapter import worker_adapter  # Используем Worker вместо IMDbService

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

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

        data = content_data.model_dump()
        cast = data.pop("cast", None)

        content = Content(**data)
        if cast is not None:
            content.actors_cast = cast

        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        logger.info(f"Created new content: {content.title}")
        return content

    async def search_omdb_direct(
        self,
        title: str,
        content_type: str = None
    ) -> Dict[str, Any]:
        """Упрощенная версия поиска для бота

        Если контент уже есть в базе (просмотренный), возвращаем его первым,
        а далее добавляем до четырех результатов из OMDB, чтобы бот показал
        до пяти карточек.
        """
        try:
            # 1. Простой поиск в базе
            stmt = select(Content).where(Content.title.ilike(f"%{title}%"))

            if content_type:
                stmt = stmt.where(Content.content_type == content_type)

            result = await self.db.execute(stmt)
            # Если найдено несколько записей, берем первую, чтобы не падать с ошибкой
            content = result.scalars().first()

            db_item = None
            if content:
                db_item = {
                    **self._content_to_dict(content),
                    "source": "database",
                    "already_watched": True,
                }

            # 2. Ищем через Worker (получаем список до 5 элементов)
            worker_result = await worker_adapter.search_omdb(title, content_type) or []

            omdb_items = []
            seen_imdb_ids = set()

            if db_item and db_item.get("imdb_id"):
                seen_imdb_ids.add(db_item["imdb_id"])

            for item in worker_result:
                imdb_id = item.get("imdb_id")
                if imdb_id and imdb_id in seen_imdb_ids:
                    continue
                if imdb_id:
                    seen_imdb_ids.add(imdb_id)
                omdb_items.append({**item, "source": "omdb", "already_watched": False})

                if len(omdb_items) >= 4:
                    break

            # 3. Составляем итоговый список (до 5 элементов)
            combined: list = []
            if db_item:
                combined.append(db_item)

            combined.extend(omdb_items)

            if combined:
                return {
                    "source": "mixed" if db_item and omdb_items else (db_item and "database") or "omdb",
                    "data": combined,
                    "message": "Найдены результаты поиска"
                }

            return {
                "source": "not_found",
                "data": None,
                "message": f"'{title}' не найден в OMDB"
            }

        except Exception as e:
            logger.error(f"Error in search_omdb_direct: {e}")
            return {
                "source": "error",
                "data": None,
                "message": f"Ошибка поиска: {str(e)}"
            }

    async def add_from_omdb(
        self,
        title: str,
        content_type: str = "movie"
    ) -> Dict[str, Any]:
        """Добавить фильм из OMDB через Worker"""
        try:
            # Ищем через Worker
            worker_result = await worker_adapter.search_omdb(title, content_type)
            
            if not worker_result:
                return {
                    "success": False,
                    "error": f"'{title}' не найден в OMDB",
                    "content": None
                }
            
            # Проверяем, существует ли уже контент с таким IMDb ID
            if worker_result.get('imdb_id'):
                existing_content = await self.get_content_by_imdb_id(worker_result['imdb_id'])
                if existing_content:
                    return {
                        "success": True,
                        "message": "Уже существует в базе",
                        "content": self._content_to_dict(existing_content)
                    }
            
            # Создаем объект контента
            content_data = ContentCreate(**worker_result)
            content = await self.create_content(content_data)
            
            return {
                "success": True,
                "message": "Успешно добавлен из OMDB",
                "content": self._content_to_dict(content)
            }
            
        except Exception as e:
            logger.error(f"Error adding from OMDB: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    def _content_to_dict(self, content: Content) -> Dict[str, Any]:
        """Конвертировать Content в словарь"""
        if not content:
            return {}
            
        return {
            "id": content.id,
            "title": content.title,
            "original_title": content.original_title,
            "description": content.description,
            "content_type": content.content_type,
            "release_year": content.release_year,
            "duration_minutes": content.duration_minutes,
            "imdb_rating": content.imdb_rating,
            "imdb_id": content.imdb_id,
            "poster_url": content.poster_url,
            "genre": content.genre,
            "director": content.director,
            "cast": content.actors_cast,
            "total_seasons": content.total_seasons,
        }

    # УДАЛЕННЫЕ МЕТОДЫ (лишнее):
    # - _search_in_database (не используется ботом)
    # - search_content (не используется ботом)
    # - _search_in_external_api (заменен на worker_adapter)
    # - _save_external_results (интегрировано в add_from_omdb)
    # - imdb_service в __init__ (заменен на worker_adapter)

    async def update_content(self, content_id: int, content_data: ContentUpdate) -> Optional[Content]:
        """Обновить данные контента"""
        content = await self.get_content_by_id(content_id)
        if not content:
            return None

        update_data = content_data.model_dump(exclude_unset=True)
        cast = update_data.pop("cast", None)

        for field, value in update_data.items():
            setattr(content, field, value)

        if cast is not None:
            content.actors_cast = cast

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