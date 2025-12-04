import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

class Scheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    async def send_daily_reminder(self):
        """Отправка ежедневного напоминания"""
        # Здесь будет логика отправки напоминаний
        # Пока заглушка
        pass

    async def send_weekly_report(self):
        """Отправка еженедельного отчета"""
        # Здесь будет логика отправки отчетов
        # Пока заглушка
        pass

    async def start(self):
        """Запуск планировщика"""
        # Ежедневное напоминание в 20:00
        self.scheduler.add_job(
            self.send_daily_reminder,
            CronTrigger(hour=20, minute=0),
            id='daily_reminder'
        )

        # Еженедельный отчет в понедельник в 10:00
        self.scheduler.add_job(
            self.send_weekly_report,
            CronTrigger(day_of_week=0, hour=10, minute=0),
            id='weekly_report'
        )

        self.scheduler.start()