# telegram_bot/app/services/omdb_client.py
import httpx
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class OMDbClient:
    def __init__(self):
        self.base_url = "http://www.omdbapi.com/"
        self.api_key = os.getenv("OMDB_API_KEY", "")
        
        if not self.api_key:
            logger.warning("⚠️ OMDB_API_KEY не установлен. Поиск по OMDB будет недоступен.")
    
    async def search_by_title(self, title: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Поиск по названию в OMDB"""
        if not self.api_key:
            return None
        
        try:
            params = {
                "apikey": self.api_key,
                "t": title,
                "plot": "short"
            }
            
            if content_type:
                params["type"] = content_type
            
            logger.info(f"🔍 Ищем в OMDB: '{title}' ({content_type})")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("Response") == "True":
                        logger.info(f"✅ Найден в OMDB: {data.get('Title')}")
                        return self._parse_response(data)
                    else:
                        logger.warning(f"❌ Не найден в OMDB: {data.get('Error')}")
                        return None
                else:
                    logger.error(f"❌ Ошибка OMDB API: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"💥 Ошибка при запросе к OMDB: {e}")
            return None
    
    async def search_multiple(self, title: str) -> Optional[Dict[str, Any]]:
        """Поиск фильма, потом сериала"""
        # Сначала ищем фильм
        result = await self.search_by_title(title, "movie")
        if result:
            return result
        
        # Потом ищем сериал
        return await self.search_by_title(title, "series")
    
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг ответа от OMDB API (аналогично вашему IMDbService)"""
        content_type = "movie"
        if data.get("Type") == "series":
            content_type = "series"

        # Парсим продолжительность
        duration_minutes = None
        if data.get("Runtime") and data.get("Runtime") != "N/A":
            try:
                duration_minutes = int(data["Runtime"].split(" ")[0])
            except (ValueError, IndexError):
                pass

        # Парсим рейтинг
        imdb_rating = None
        if data.get("imdbRating") and data.get("imdbRating") != "N/A":
            try:
                imdb_rating = float(data["imdbRating"])
            except ValueError:
                pass

        # Парсим год
        release_year = None
        if data.get("Year") and data.get("Year") != "N/A":
            try:
                year_str = data["Year"].split("–")[0]
                release_year = int(year_str)
            except ValueError:
                pass

        return {
            "title": data.get("Title"),
            "original_title": data.get("Title"),
            "description": data.get("Plot"),
            "content_type": content_type,
            "release_year": release_year,
            "duration_minutes": duration_minutes,
            "imdb_rating": imdb_rating,
            "imdb_id": data.get("imdbID"),
            "poster_url": data.get("Poster") if data.get("Poster") != "N/A" else None,
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "cast": data.get("Actors"),
            "total_seasons": int(data["totalSeasons"]) if data.get("totalSeasons") and data.get("totalSeasons") != "N/A" else None,
            "omdb_data": data  # Сохраняем полные данные
        }
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """Форматирование для показа пользователю"""
        title = data.get("title", "Неизвестно")
        year = data.get("release_year", "Неизвестно")
        imdb_rating = data.get("imdb_rating", "Нет")
        genre = data.get("genre", "Неизвестно")
        director = data.get("director", "Неизвестно")
        cast = data.get("cast", "Неизвестно")
        description = data.get("description", "Нет описания")
        content_type = "фильм" if data.get("content_type") == "movie" else "сериал"
        
        return (
            f"🎬 <b>{title}</b> ({year})\n"
            f"📺 Тип: {content_type}\n"
            f"⭐ IMDb: {imdb_rating}/10\n"
            f"🎭 Жанр: {genre}\n"
            f"🎥 Режиссер: {director}\n"
            f"👥 В ролях: {cast}\n"
            f"📖 Описание: {description}\n"
            f"\nДобавить этот {content_type}?"
        )

# Глобальный экземпляр
omdb_client = OMDbClient()