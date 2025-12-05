# telegram_bot/app/services/content_service.py
import logging
from typing import Optional, Dict, Any
from app.services.api_client import api_client

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        self.api_client = api_client
    
    async def search_content(self, title: str, content_type: str = None) -> Dict[str, Any]:
        """Поиск для бота через API"""
        params = {"title": title}
        if content_type:
            params["content_type"] = content_type
        
        # Бот вызывает специальный endpoint для бота
        response = await self.api_client.get("/api/v1/bot/search", params=params)
        
        if not response:
            return {
                "found_in_db": False,
                "found_in_omdb": False,
                "formatted_text": f"❌ Ошибка при поиске '{title}'"
            }
        
        if response["source"] == "database":
            return {
                "found_in_db": True,
                "found_in_omdb": False,
                "db_content": response["data"],
                "formatted_text": f"✅ Найден в базе: <b>{response['data']['title']}</b>"
            }
        elif response["source"] == "omdb":
            return {
                "found_in_db": False,
                "found_in_omdb": True,
                "omdb_content": response["data"],
                "formatted_text": self._format_omdb_result(response["data"])
            }
        else:
            return {
                "found_in_db": False,
                "found_in_omdb": False,
                "formatted_text": f"❌ Не найден: '{title}'"
            }
    
    async def add_from_omdb(self, title: str, content_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Добавить контент из OMDB через API"""
        data = {
            "title": title,
            "content_type": content_type
        }
        
        response = await self.api_client.post("/api/v1/bot/add-from-omdb", data=data)
        
        if response and response.get("success"):
            return response.get("content")
        return None
    
    def _format_omdb_result(self, omdb_data: Dict[str, Any]) -> str:
        """Форматирование результата из OMDB для показа пользователю"""
        if not omdb_data:
            return "❌ Нет данных о фильме"
        
        title = omdb_data.get("title", "Неизвестно")
        year = omdb_data.get("release_year", "Неизвестно")
        imdb_rating = omdb_data.get("imdb_rating", "Нет")
        genre = omdb_data.get("genre", "Неизвестно")
        director = omdb_data.get("director", "Неизвестно")
        cast = omdb_data.get("cast", "Неизвестно")
        description = omdb_data.get("description", "Нет описания")
        
        # Обрезаем длинное описание
        if len(description) > 200:
            description = description[:200] + "..."
        
        # Определяем тип контента
        content_type = omdb_data.get("content_type", "movie")
        type_text = "фильм" if content_type == "movie" else "сериал"
        
        return (
            f"🎬 <b>{title}</b> ({year})\n"
            f"📺 Тип: {type_text}\n"
            f"⭐ IMDb: {imdb_rating}/10\n"
            f"🎭 Жанр: {genre}\n"
            f"🎥 Режиссер: {director}\n"
            f"👥 В ролях: {cast}\n"
            f"📖 Описание: {description}\n"
            f"\nДобавить этот {type_text} в нашу базу?"
        )