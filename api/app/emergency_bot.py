# api/app/emergency_bot.py
from fastapi import APIRouter
from typing import Optional

emergency_router = APIRouter()

@emergency_router.get("/search")
async def emergency_search(title: str, content_type: Optional[str] = None):
    return {
        "emergency": True,
        "title": title,
        "data": {"id": 1, "title": title}
    }

@emergency_router.get("/test")
async def emergency_test():
    return {"status": "EMERGENCY MODE"}