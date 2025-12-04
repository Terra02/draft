from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.services.analytics_service import AnalyticsService
from app.utils.formatters import format_analytics_message
from app.utils.text_templates import get_analytics_message

router = Router()

@router.message(Command("analytics"))
@router.message(F.text == "📈 Аналитика")
async def cmd_analytics(message: types.Message, state: FSMContext):
    """Показать аналитику"""
    await state.clear()

    analytics_service = AnalyticsService()
    analytics = await analytics_service.get_user_analytics(
        telegram_id=message.from_user.id,
        days=30
    )

    text = get_analytics_message(analytics)
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: types.Message):
    """Показать подробную статистику"""
    analytics_service = AnalyticsService()
    stats = await analytics_service.get_user_detailed_stats(
        telegram_id=message.from_user.id
    )

    text = format_analytics_message(stats)
    
    await message.answer(text, parse_mode="HTML")