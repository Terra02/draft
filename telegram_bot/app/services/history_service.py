from typing import Optional, Dict, Any, List
from app.services.api_client import api_client

class HistoryService:
    def __init__(self):
        self.api_client = api_client

    async def get_user_history(self, telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить историю пользователя"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return []
            
        return await self.api_client.get(f"/api/v1/history/user/{user['id']}?limit={limit}")

    async def get_history_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Получить запись истории по ID"""
        return await self.api_client.get(f"/api/v1/history/{record_id}")

    async def add_view_history(self, telegram_id: int, content_id: int, 
                             rating: Optional[float] = None, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Добавить запись в историю просмотров"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return None
            
        history_data = {
            "user_id": user["id"],
            "content_id": content_id,
            "rating": rating,
            "notes": notes
        }
        ##поменял endpoint
        return await self.api_client.post("/api/v1/view-history/", data=history_data)

    async def update_rating(self, record_id: int, rating: float) -> Optional[Dict[str, Any]]:
        """Обновить рейтинг записи"""
        return await self.api_client.put(f"/api/v1/history/{record_id}", data={"rating": rating})