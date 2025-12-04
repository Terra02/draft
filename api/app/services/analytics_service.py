from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, text
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from app.models.user import User
from app.models.content import Content
from app.models.view_history import ViewHistory
from app.models.watchlist import Watchlist

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_analytics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Получить аналитику пользователя за период"""
        # Основная статистика
        total_views_stmt = select(func.count()).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at.between(start_date, end_date)
            )
        )
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        # Статистика по типам контента
        content_type_stmt = select(
            Content.content_type,
            func.count(ViewHistory.id)
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at.between(start_date, end_date)
            )
        ).group_by(Content.content_type)

        content_type_result = await self.db.execute(content_type_stmt)
        content_type_stats = dict(content_type_result.all())

        # Средний рейтинг
        avg_rating_stmt = select(func.avg(ViewHistory.rating)).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.rating.isnot(None),
                ViewHistory.watched_at.between(start_date, end_date)
            )
        )
        avg_rating_result = await self.db.execute(avg_rating_stmt)
        avg_rating = round(avg_rating_result.scalar() or 0, 2)

        # Самые просматриваемые жанры
        genre_stmt = select(
            Content.genre,
            func.count(ViewHistory.id).label('count')
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at.between(start_date, end_date),
                Content.genre.isnot(None)
            )
        ).group_by(Content.genre).order_by(desc('count')).limit(5)

        genre_result = await self.db.execute(genre_stmt)
        top_genres = [{"genre": row[0], "count": row[1]} for row in genre_result]

        # Ежемесячная статистика
        monthly_stats = await self._get_monthly_stats(user_id, start_date, end_date)

        return {
            "total_views": total_views,
            "movies_views": content_type_stats.get('movie', 0),
            "series_views": content_type_stats.get('series', 0),
            "average_rating": avg_rating,
            "top_genres": top_genres,
            "monthly_stats": monthly_stats,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }

    async def _get_monthly_stats(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Получить ежемесячную статистику"""
        monthly_stmt = text("""
            SELECT 
                DATE_TRUNC('month', watched_at) as month,
                COUNT(*) as view_count,
                AVG(rating) as avg_rating
            FROM view_history 
            WHERE user_id = :user_id 
                AND watched_at BETWEEN :start_date AND :end_date
            GROUP BY DATE_TRUNC('month', watched_at)
            ORDER BY month
        """)

        result = await self.db.execute(
            monthly_stmt, 
            {"user_id": user_id, "start_date": start_date, "end_date": end_date}
        )
        
        monthly_stats = []
        for row in result:
            monthly_stats.append({
                "month": row[0],
                "view_count": row[1],
                "average_rating": float(row[2]) if row[2] else None
            })
        
        return monthly_stats

    async def get_user_timeline_analytics(self, user_id: int, period: str = "monthly") -> Dict[str, Any]:
        """Получить временную аналитику пользователя"""
        if period == "daily":
            group_by = "DATE(watched_at)"
        elif period == "weekly":
            group_by = "DATE_TRUNC('week', watched_at)"
        elif period == "yearly":
            group_by = "DATE_TRUNC('year', watched_at)"
        else:  # monthly
            group_by = "DATE_TRUNC('month', watched_at)"

        timeline_stmt = text(f"""
            SELECT 
                {group_by} as period,
                COUNT(*) as view_count,
                AVG(rating) as avg_rating
            FROM view_history 
            WHERE user_id = :user_id
            GROUP BY {group_by}
            ORDER BY period
        """)

        result = await self.db.execute(timeline_stmt, {"user_id": user_id})
        
        timeline_data = []
        for row in result:
            timeline_data.append({
                "period": row[0],
                "view_count": row[1],
                "average_rating": float(row[2]) if row[2] else None
            })
        
        return {
            "period": period,
            "data": timeline_data
        }

    async def get_content_analytics(self) -> Dict[str, Any]:
        """Получить аналитику контента"""
        # Самые просматриваемые фильмы
        top_movies_stmt = select(
            Content.title,
            Content.content_type,
            func.count(ViewHistory.id).label('view_count'),
            func.avg(ViewHistory.rating).label('avg_rating')
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            Content.content_type == 'movie'
        ).group_by(
            Content.id, Content.title, Content.content_type
        ).order_by(desc('view_count')).limit(10)

        top_movies_result = await self.db.execute(top_movies_stmt)
        top_movies = [
            {
                "title": row[0],
                "content_type": row[1],
                "view_count": row[2],
                "average_rating": float(row[3]) if row[3] else None
            }
            for row in top_movies_result
        ]

        # Самые просматриваемые сериалы
        top_series_stmt = select(
            Content.title,
            Content.content_type,
            func.count(ViewHistory.id).label('view_count'),
            func.avg(ViewHistory.rating).label('avg_rating')
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            Content.content_type == 'series'
        ).group_by(
            Content.id, Content.title, Content.content_type
        ).order_by(desc('view_count')).limit(10)

        top_series_result = await self.db.execute(top_series_stmt)
        top_series = [
            {
                "title": row[0],
                "content_type": row[1],
                "view_count": row[2],
                "average_rating": float(row[3]) if row[3] else None
            }
            for row in top_series_result
        ]

        # Контент с наивысшим рейтингом
        top_rated_stmt = select(
            Content.title,
            Content.content_type,
            func.avg(ViewHistory.rating).label('avg_rating'),
            func.count(ViewHistory.id).label('view_count')
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            ViewHistory.rating.isnot(None)
        ).group_by(
            Content.id, Content.title, Content.content_type
        ).having(
            func.count(ViewHistory.id) >= 3  # Минимум 3 оценки
        ).order_by(desc('avg_rating')).limit(10)

        top_rated_result = await self.db.execute(top_rated_stmt)
        top_rated = [
            {
                "title": row[0],
                "content_type": row[1],
                "average_rating": float(row[2]) if row[2] else None,
                "view_count": row[3]
            }
            for row in top_rated_result
        ]

        return {
            "most_watched_movies": top_movies,
            "most_watched_series": top_series,
            "highest_rated_content": top_rated
        }

    async def get_system_overview(self) -> Dict[str, Any]:
        """Получить обзор системы"""
        # Общее количество пользователей
        total_users_stmt = select(func.count(User.id))
        total_users_result = await self.db.execute(total_users_stmt)
        total_users = total_users_result.scalar() or 0

        # Активные пользователи (просмотрели что-то за последние 30 дней)
        active_users_stmt = select(func.count(func.distinct(ViewHistory.user_id))).where(
            ViewHistory.watched_at >= datetime.now() - timedelta(days=30)
        )
        active_users_result = await self.db.execute(active_users_stmt)
        active_users = active_users_result.scalar() or 0

        # Общее количество контента
        total_content_stmt = select(func.count(Content.id))
        total_content_result = await self.db.execute(total_content_stmt)
        total_content = total_content_result.scalar() or 0

        # Общее количество просмотров
        total_views_stmt = select(func.count(ViewHistory.id))
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        # Распределение по типам контента
        content_types_stmt = select(
            Content.content_type,
            func.count(Content.id)
        ).group_by(Content.content_type)
        
        content_types_result = await self.db.execute(content_types_stmt)
        content_types = dict(content_types_result.all())

        # Активность пользователей (последние 7 дней)
        weekly_activity_stmt = select(
            func.date(ViewHistory.watched_at).label('date'),
            func.count(ViewHistory.id).label('view_count')
        ).where(
            ViewHistory.watched_at >= datetime.now() - timedelta(days=7)
        ).group_by(
            func.date(ViewHistory.watched_at)
        ).order_by(desc('date'))

        weekly_activity_result = await self.db.execute(weekly_activity_stmt)
        user_activity = {str(row[0]): row[1] for row in weekly_activity_result}

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_content": total_content,
            "total_views": total_views,
            "content_types": content_types,
            "user_activity": user_activity
        }