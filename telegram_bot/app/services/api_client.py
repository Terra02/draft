import httpx
import logging
from typing import Optional, Dict, Any, List

from app.config import settings

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = settings.API_URL.rstrip('/')  # "http://api:8000"
        self.api_prefix = settings.API_PREFIX
        self.client = httpx.AsyncClient(timeout=30.0)  # УБРАТЬ base_url=!
        logger.info(f"✅ APIClient initialized. Base URL: {self.base_url}")

    async def request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Выполнить запрос к API"""
        if not endpoint.startswith(self.api_prefix):
            endpoint = f"{self.api_prefix}{endpoint}"
            
        # Убедимся что endpoint начинается с /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"🌐 {method} {url}")
        if kwargs.get('params'):
            logger.info(f"📤 Params: {kwargs['params']}")
        if kwargs.get('json'):
            logger.info(f"📦 JSON: {kwargs['json']}")
        
        try:
            response = await self.client.request(method, url, **kwargs)
            logger.info(f"📥 Response status: {response.status_code}")
            logger.info(f"📄 Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Логируем первые 500 символов ответа
            text = response.text
            logger.info(f"📋 Response text (first 500 chars): {text[:500]}")
            
            data = response.json()
            logger.info(f"✅ Response parsed as JSON")
            logger.info(f"📊 Response type: {type(data)}")
            if isinstance(data, dict):
                logger.info(f"🔑 Dict keys: {list(data.keys())}")
            elif isinstance(data, list):
                logger.info(f"📈 List length: {len(data)}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error: {e.response.status_code}")
            logger.error(f"❌ Response: {e.response.text[:500]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"❌ Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """GET запрос"""
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """POST запрос"""
        return await self.request("POST", endpoint, json=data)

    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """PUT запрос"""
        return await self.request("PUT", endpoint, json=data)

    async def delete(self, endpoint: str) -> bool:
        """DELETE запрос"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.delete(url)
            logger.info(f"DELETE {url} -> {response.status_code}")
            return response.status_code == 204
        except httpx.HTTPError as e:
            logger.error(f"DELETE error: {e}")
            return False

api_client = APIClient()