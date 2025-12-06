# telegram_bot/app/services/api_client.py
import httpx
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        # Используем переменную окружения напрямую
        self.base_url = os.getenv("API_URL", "http://api:8000")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    async def request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Выполнить запрос к API"""
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            # Возвращаем тело ответа даже при ошибочных статусах, чтобы бот мог показать причину
            if response.is_success:
                if response.status_code == 204:
                    return {"success": True}
                return response.json()

            try:
                error_body = response.json()
            except Exception:
                error_body = {"detail": response.text}

            return {
                "success": False,
                "status_code": response.status_code,
                **(error_body if isinstance(error_body, dict) else {"error": str(error_body)}),
            }
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return {"success": False, "error": str(e)}

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """GET запрос"""
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """POST запрос"""
        return await self.request("POST", endpoint, json=data)

    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """PUT запрос"""
        return await self.request("PUT", endpoint, json=data)

    async def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """DELETE запрос"""
        return await self.request("DELETE", endpoint)

    async def close(self):
        """Закрыть клиент"""
        await self.client.aclose()

# Глобальный экземпляр клиента API
api_client = APIClient()