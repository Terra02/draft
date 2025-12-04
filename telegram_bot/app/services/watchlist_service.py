from typing import Optional, Dict, Any, List
from app.services.api_client import api_client

class WatchlistService:
    def __init__(self):
        self.api_client = api_client

    async def get_user_watchlist(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получить список желаемого пользователя"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return []
            
        return await self.api_client.get(f"/api/v1/watchlist/user/{user['id']}")

    async def add_to_watchlist(self, telegram_id: int, content_id: int, 
                             priority: int = 1, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Добавить контент в список желаемого"""
        user = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if not user:
            return None
            
        watchlist_data = {
            "user_id": user["id"],
            "content_id": content_id,
            "priority": priority,
            "notes": notes
        }
        
        return await self.api_client.post("/api/v1/watchlist/", data=watchlist_data)

    async def remove_from_watchlist(self, item_id: int) -> bool:
        """Удалить из списка желаемого"""
        return await self.api_client.delete(f"/api/v1/watchlist/{item_id}")