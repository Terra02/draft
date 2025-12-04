from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import Optional, List, Dict, Any
import logging

from app.models.watchlist import Watchlist
from app.models.content import Content
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate

logger = logging.getLogger(__name__)

class WatchlistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_watchlist_by_id(self, watchlist_id: int) -> Optional[Watchlist]:
        """Получить запись watchlist по ID"""
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        return result.scalar_one_or_none()

    async def create_watchlist(self, watchlist_data: WatchlistCreate) -> Watchlist:
        """Создать новую запись в watchlist"""
        # Проверяем, существует ли уже такая запись
        existing = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == watchlist_data.user_id,
                    Watchlist.content_id == watchlist_data.content_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Content already in watchlist")

        watchlist = Watchlist(**watchlist_data.model_dump())
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        logger.info(f"Added content {watchlist_data.content_id} to user {watchlist_data.user_id} watchlist")
        return watchlist

    async def update_watchlist(self, watchlist_id: int, watchlist_data: WatchlistUpdate) -> Optional[Watchlist]:
        """Обновить запись watchlist"""
        watchlist = await self.get_watchlist_by_id(watchlist_id)
        if not watchlist:
            return None

        update_data = watchlist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(watchlist, field, value)

        await self.db.commit()
        await self.db.refresh(watchlist)
        logger.info(f"Updated watchlist record {watchlist_id}")
        return watchlist

    async def delete_watchlist(self, watchlist_id: int) -> bool:
        """Удалить запись из watchlist"""
        watchlist = await self.get_watchlist_by_id(watchlist_id)
        if not watchlist:
            return False

        await self.db.delete(watchlist)
        await self.db.commit()
        logger.info(f"Removed content from watchlist: {watchlist_id}")
        return True

    async def get_user_watchlist(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Watchlist]:
        """Получить watchlist пользователя"""
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .order_by(desc(Watchlist.added_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_watchlist_with_content(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получить watchlist пользователя с информацией о контенте"""
        result = await self.db.execute(
            select(Watchlist, Content)
            .join(Content, Watchlist.content_id == Content.id)
            .where(Watchlist.user_id == user_id)
            .order_by(desc(Watchlist.added_at))
            .offset(skip)
            .limit(limit)
        )
        
        watchlist_with_content = []
        for watchlist, content in result:
            watchlist_dict = {
                **watchlist.__dict__,
                "content_title": content.title,
                "content_type": content.content_type,
                "content": content.__dict__
            }
            watchlist_with_content.append(watchlist_dict)
        
        return watchlist_with_content

    async def is_content_in_watchlist(self, user_id: int, content_id: int) -> bool:
        """Проверить, есть ли контент в watchlist пользователя"""
        result = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.content_id == content_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_watchlist_count(self, user_id: int) -> int:
        """Получить количество элементов в watchlist пользователя"""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).where(Watchlist.user_id == user_id)
        )
        return result.scalar() or 0