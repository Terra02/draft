import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import os

from app.tasks.update_ratings import update_ratings_task
from app.tasks.cleanup import cleanup_task
from app.tasks.statistics import update_statistics_task
from app.tasks.notifications import send_notifications_task
from app.utils.logger import setup_logging
from app.utils.config import get_settings

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.settings = get_settings()
        self.is_running = False

    async def start(self):
        """Запуск воркера"""
        if self.is_running:
            logger.warning("Worker is already running")
            return

        logger.info("🚀 Starting Movie Tracker Worker...")
        self.is_running = True

        try:
            # Регистрация периодических задач
            self.scheduler.add_job(
                self._safe_execute(update_ratings_task),
                CronTrigger(hour=3, minute=0),  # Каждый день в 3:00
                id='update_ratings',
                name='Обновление рейтингов контента'
            )

            self.scheduler.add_job(
                self._safe_execute(cleanup_task),
                CronTrigger(hour=4, minute=0),  # Каждый день в 4:00
                id='cleanup',
                name='Очистка старых данных'
            )

            self.scheduler.add_job(
                self._safe_execute(update_statistics_task),
                CronTrigger(hour=2, minute=0),  # Каждый день в 2:00
                id='update_statistics',
                name='Обновление статистики'
            )

            self.scheduler.add_job(
                self._safe_execute(send_notifications_task),
                CronTrigger(hour=9, minute=0),  # Каждый день в 9:00
                id='send_notifications',
                name='Отправка уведомлений'
            )

            # Запуск планировщика
            self.scheduler.start()
            logger.info("✅ Worker started successfully with scheduled tasks")

            # Бесконечный цикл
            while self.is_running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"❌ Worker error: {e}")
            self.is_running = False
            raise

    def _safe_execute(self, task_func):
        """Обертка для безопасного выполнения задач"""
        async def wrapper():
            try:
                logger.info(f"Starting task: {task_func.__name__}")
                await task_func()
                logger.info(f"Completed task: {task_func.__name__}")
            except Exception as e:
                logger.error(f"Task {task_func.__name__} failed: {e}")
        return wrapper

    async def stop(self):
        """Остановка воркера"""
        logger.info("🛑 Stopping worker...")
        self.is_running = False
        self.scheduler.shutdown()
        logger.info("✅ Worker stopped successfully")

async def main():
    worker = Worker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Worker fatal error: {e}")
    finally:
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())