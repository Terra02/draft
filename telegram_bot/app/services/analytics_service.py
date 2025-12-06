from typing import Optional, Dict, Any
from app.services.api_client import api_client

class AnalyticsService:
    def __init__(self):
        self.api_client = api_client

    async def get_user_analytics(self, telegram_id: int, days: int = 30) -> Optional[Dict[str, Any]]:
        """Получить аналитику пользователя"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return None
            
        return await self.api_client.get(f"/api/v1/analytics/user/{user['id']}?days={days}")

    async def get_user_detailed_stats(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить подробную статистику пользователя"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return None
            
        return await self.api_client.get(
            f"/api/v1/view-history/user/{user['id']}/stats"
        )