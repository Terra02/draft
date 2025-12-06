import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.handlers import (
    start, help, view_history, watchlist,
    search, analytics, settings as settings_handlers
)
from app.utils.scheduler import Scheduler

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(view_history.router)
    dp.include_router(watchlist.router)
    dp.include_router(search.router)
    dp.include_router(analytics.router)
    dp.include_router(settings_handlers.router)

    # Запуск планировщика для уведомлений
    scheduler = Scheduler(bot)
    await scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())