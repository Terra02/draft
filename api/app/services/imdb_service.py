import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class IMDbService:
    def __init__(self):
        self.base_url = "http://www.omdbapi.com/"
        self.api_key = settings.omdb_api_key

    async def search_content(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Поиск контента в OMDb API"""
        if not self.api_key:
            logger.warning("OMDb API key not configured")
            return None

        params = {
            "apikey": self.api_key,
            "t": title,
            "type": "movie"
        }
        
        if year:
            params["y"] = year

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("Response") == "True":
                    return self._parse_omdb_response(data)
                else:
                    logger.warning(f"OMDb API error: {data.get('Error')}")
                    return None

        except httpx.RequestError as e:
            logger.error(f"OMDb API request failed: {e}")
            return None

    async def get_content_by_imdb_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о контенте по IMDb ID"""
        if not self.api_key:
            logger.warning("OMDb API key not configured")
            return None

        params = {
            "apikey": self.api_key,
            "i": imdb_id
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("Response") == "True":
                    return self._parse_omdb_response(data)
                else:
                    logger.warning(f"OMDb API error: {data.get('Error')}")
                    return None

        except httpx.RequestError as e:
            logger.error(f"OMDb API request failed: {e}")
            return None

    def _parse_omdb_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг ответа от OMDb API"""
        # Определяем тип контента
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
                # Год может быть в формате "2010-2015" для сериалов
                year_str = data["Year"].split("–")[0]
                release_year = int(year_str)
            except ValueError:
                pass

        return {
            "title": data.get("Title"),
            "original_title": data.get("Title"),  # OMDb не предоставляет оригинальное название
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
            "total_seasons": int(data["totalSeasons"]) if data.get("totalSeasons") and data.get("totalSeasons") != "N/A" else None
        }