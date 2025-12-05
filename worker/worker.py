# worker/app/main.py
from fastapi import FastAPI, HTTPException
import httpx
import os
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="OMDB Worker")
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    title: str
    content_type: Optional[str] = None

class SearchResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class OMDBService:
    def __init__(self):
        self.api_key = os.getenv("OMDB_API_KEY")
        self.base_url = "http://www.omdbapi.com/"
        
        if not self.api_key:
            logger.error("❌ OMDB_API_KEY not configured in worker")
    
    async def search(self, title: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Поиск в OMDB API"""
        if not self.api_key:
            logger.error("OMDB API key not configured")
            return None
        
        try:
            params = {
                "apikey": self.api_key,
                "t": title,
                "plot": "short"
            }
            
            if content_type:
                params["type"] = content_type
            
            logger.info(f"🔍 Worker ищет в OMDB: {title}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("Response") == "True":
                        logger.info(f"✅ Worker нашел: {data.get('Title')}")
                        return self._parse_response(data)
                    else:
                        logger.warning(f"❌ Не найден в OMDB: {data.get('Error')}")
                        return None
                else:
                    logger.error(f"❌ OMDB API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"💥 Worker error: {e}")
            return None
    
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг ответа OMDB"""
        content_type = "movie"
        if data.get("Type") == "series":
            content_type = "series"
        
        # Парсим год
        release_year = None
        if data.get("Year") and data.get("Year") != "N/A":
            try:
                year_str = data["Year"].split("–")[0]
                release_year = int(year_str)
            except ValueError:
                pass
        
        # Парсим рейтинг
        imdb_rating = None
        if data.get("imdbRating") and data.get("imdbRating") != "N/A":
            try:
                imdb_rating = float(data["imdbRating"])
            except ValueError:
                pass
        
        return {
            "title": data.get("Title"),
            "original_title": data.get("Title"),
            "description": data.get("Plot"),
            "content_type": content_type,
            "release_year": release_year,
            "imdb_rating": imdb_rating,
            "imdb_id": data.get("imdbID"),
            "poster_url": data.get("Poster") if data.get("Poster") != "N/A" else None,
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "cast": data.get("Actors"),
            "total_seasons": int(data["totalSeasons"]) if data.get("totalSeasons") and data.get("totalSeasons") != "N/A" else None
        }

# Инициализация сервиса
omdb_service = OMDBService()

@app.post("/search", response_model=SearchResponse)
async def search_omdb(request: SearchRequest):
    """Endpoint для поиска в OMDB"""
    if not omdb_service.api_key:
        return SearchResponse(
            success=False,
            error="OMDB API key not configured in worker"
        )
    
    result = await omdb_service.search(request.title, request.content_type)
    
    if result:
        return SearchResponse(success=True, data=result)
    else:
        return SearchResponse(
            success=False,
            error=f"Фильм '{request.title}' не найден в OMDB"
        )

@app.get("/health")
async def health_check():
    """Проверка здоровья worker"""
    return {"status": "healthy", "service": "omdb-worker"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)