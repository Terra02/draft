# api/app/services/worker_client.py
import httpx
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WorkerClient:
    def __init__(self):
        self.worker_url = os.getenv("WORKER_URL", "http://worker:8001")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_omdb(self, title: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Поиск фильма через worker"""
        try:
            logger.info(f"🔍 API запрашивает worker для поиска: {title}")
            
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
                    logger.info(f"✅ Worker нашел: {result['data'].get('title')}")
                    return result["data"]
                else:
                    logger.warning(f"❌ Worker не нашел: {result.get('error')}")
                    return None
            else:
                logger.error(f"❌ Worker error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Ошибка связи с worker: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()

# Глобальный экземпляр
worker_client = WorkerClient()