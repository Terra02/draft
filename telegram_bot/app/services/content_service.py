# app/services/content_service.py - ВРЕМЕННО замените на:
from typing import Optional, Dict, Any, List
import traceback
import logging

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        from app.services.api_client import api_client
        self.api_client = api_client
        logger.info(f"🎯 ContentService initialized")

    async def search_content(self, query: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Поиск контента"""
        logger.info(f"🔍 SEARCH STARTED for: '{query}'")
        
        params = {"query": query}
        if content_type:
            params["content_type"] = content_type
            
        logger.info(f"📤 API call: /api/v1/content/search, params: {params}")
        
        try:
            response = await self.api_client.get("/api/v1/content/search", params=params)
            logger.info(f"📥 API response type: {type(response)}")
            
            if response is None:
                logger.warning("⚠️ API returned None")
                return []
            
            # ДЕТАЛЬНАЯ ОТЛАДКА СТРУКТУРЫ ОТВЕТА
            logger.info(f"📊 Full response structure:")
            if isinstance(response, dict):
                for key, value in response.items():
                    logger.info(f"   🔑 {key}: {type(value)} = {str(value)[:100]}")
            elif isinstance(response, list):
                logger.info(f"   📈 List with {len(response)} items")
                if response:
                    logger.info(f"   🎬 First item type: {type(response[0])}")
                    if isinstance(response[0], dict):
                        logger.info(f"   🎬 First item keys: {list(response[0].keys())}")
            
            # Извлекаем результаты
            if isinstance(response, dict):
                results = response.get("results", [])
                logger.info(f"✅ Extracted {len(results)} results from 'results' key")
                return results
            elif isinstance(response, list):
                logger.info(f"✅ API returned list directly, {len(response)} items")
                return response
            else:
                logger.error(f"❓ Unknown response type: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"💥 Exception in search_content: {e}")
            traceback.print_exc()
            return []