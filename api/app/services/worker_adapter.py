# api/app/services/worker_adapter.py
import httpx
import logging
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class WorkerAdapter:
    """Адаптер для работы с Worker сервисом"""
    
    def __init__(self):
        self.worker_url = os.getenv("WORKER_URL", "http://worker:8001")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_omdb(self, title: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Поиск фильма/сериала через Worker"""
        try:
            logger.info(f"🔍 WorkerAdapter ищет: {title}")
            
            payload = {
                "title": title,
                "content_type": content_type
            }
            
            response = await self.client.post(
                f"{self.worker_url}/search",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    logger.info(f"✅ WorkerAdapter нашел: {result['data'].get('title')}")
                    return result["data"]
                else:
                    logger.warning(f"❌ WorkerAdapter не нашел: {result.get('error')}")
                    return None
            else:
                logger.error(f"❌ WorkerAdapter error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Ошибка WorkerAdapter: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()

# Создаем глобальный экземпляр
worker_adapter = WorkerAdapter()