from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.view_history import ViewHistory
from app.models.content import Content
from app.schemas.view_history import ViewHistoryCreate, ViewHistoryUpdate

logger = logging.getLogger(__name__)

class ViewHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_view_history_by_id(self, history_id: int) -> Optional[ViewHistory]:
        """Получить запись истории просмотра по ID"""
        result = await self.db.execute(
            select(ViewHistory).where(ViewHistory.id == history_id)
        )
        return result.scalar_one_or_none()

    async def create_view_history(self, history_data: ViewHistoryCreate) -> ViewHistory:
        """Создать новую запись в истории просмотров"""
        history = ViewHistory(**history_data.model_dump())
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        logger.info(f"Created view history record for user {history_data.user_id}")
        return history

    async def update_view_history(self, history_id: int, history_data: ViewHistoryUpdate) -> Optional[ViewHistory]:
        """Обновить запись истории просмотра"""
        history = await self.get_view_history_by_id(history_id)
        if not history:
            return None

        update_data = history_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(history, field, value)

        await self.db.commit()
        await self.db.refresh(history)
        logger.info(f"Updated view history record {history_id}")
        return history

    async def delete_view_history(self, history_id: int) -> bool:
        """Удалить запись истории просмотра"""
        history = await self.get_view_history_by_id(history_id)
        if not history:
            return False

        await self.db.delete(history)
        await self.db.commit()
        logger.info(f"Deleted view history record {history_id}")
        return True

    async def get_user_view_history(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[ViewHistory]:
        """Получить историю просмотров пользователя"""
        result = await self.db.execute(
            select(ViewHistory)
            .where(ViewHistory.user_id == user_id)
            .order_by(desc(ViewHistory.watched_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_view_history_with_content(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получить историю просмотров пользователя с информацией о контенте"""
        result = await self.db.execute(
            select(ViewHistory, Content)
            .join(Content, ViewHistory.content_id == Content.id)
            .where(ViewHistory.user_id == user_id)
            .order_by(desc(ViewHistory.watched_at))
            .offset(skip)
            .limit(limit)
        )
        
        history_with_content = []
        for history, content in result:
            history_dict = {
                **history.__dict__,
                "content_title": content.title,
                "content_type": content.content_type,
                "content": content.__dict__
            }
            history_with_content.append(history_dict)
        
        return history_with_content

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        # Общее количество просмотров
        total_views_stmt = select(func.count()).where(ViewHistory.user_id == user_id)
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        # Количество фильмов и сериалов
        movies_views_stmt = select(func.count()).select_from(ViewHistory).join(Content).where(
            and_(ViewHistory.user_id == user_id, Content.content_type == 'movie')
        )
        movies_views_result = await self.db.execute(movies_views_stmt)
        movies_views = movies_views_result.scalar() or 0

        series_views_stmt = select(func.count()).select_from(ViewHistory).join(Content).where(
            and_(ViewHistory.user_id == user_id, Content.content_type == 'series')
        )
        series_views_result = await self.db.execute(series_views_stmt)
        series_views = series_views_result.scalar() or 0

        # Средний рейтинг
        avg_rating_stmt = select(func.avg(ViewHistory.rating)).where(
            and_(ViewHistory.user_id == user_id, ViewHistory.rating.isnot(None))
        )
        avg_rating_result = await self.db.execute(avg_rating_stmt)
        avg_rating = round(avg_rating_result.scalar() or 0, 2)

        # Просмотры за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_views_stmt = select(func.count()).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at >= thirty_days_ago
            )
        )
        recent_views_result = await self.db.execute(recent_views_stmt)
        recent_views = recent_views_result.scalar() or 0

        return {
            "total_views": total_views,
            "movies_views": movies_views,
            "series_views": series_views,
            "average_rating": avg_rating,
            "recent_views_30_days": recent_views
        }

    async def get_recent_views(self, days: int = 7, limit: int = 10) -> List[ViewHistory]:
        """Получить недавние просмотры"""
        since_date = datetime.now() - timedelta(days=days)
        result = await self.db.execute(
            select(ViewHistory)
            .where(ViewHistory.watched_at >= since_date)
            .order_by(desc(ViewHistory.watched_at))
            .limit(limit)
        )
        return result.scalars().all()