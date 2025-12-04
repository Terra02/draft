from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from app.keyboards.history_keyboards import (
    get_history_navigation_keyboard,
    get_rating_keyboard
)
from app.keyboards.main_menu import get_main_menu_keyboard
from app.states.add_record_state import AddRecordState
from app.services.history_service import HistoryService
from app.services.content_service import ContentService
from app.utils.formatters import format_history_record
from app.utils.text_templates import get_history_message

router = Router()

@router.message(Command("history"))
@router.message(F.text == "📊 История просмотров")
async def cmd_history(message: types.Message, state: FSMContext):
    """Показать историю просмотров"""
    await state.clear()

    history_service = HistoryService()
    history = await history_service.get_user_history(
        telegram_id=message.from_user.id,
        limit=5
    )

    if not history:
        await message.answer(
            "📝 Ваша история просмотров пуста.\n"
            "Добавьте первый просмотренный фильм или сериал!",
            reply_markup=get_main_menu_keyboard()
        )
        return

    text = get_history_message(history)
    keyboard = get_history_navigation_keyboard(0, len(history), history[0]['id'])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("history_detail_"))
async def show_history_detail(callback: types.CallbackQuery):
    """Показать детали записи истории"""
    record_id = int(callback.data.split("_")[2])
    
    history_service = HistoryService()
    record = await history_service.get_history_record(record_id)
    
    if not record:
        await callback.answer("Запись не найдена")
        return

    text = format_history_record(record)
    keyboard = get_rating_keyboard(record_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@router.message(F.text == "➕ Добавить просмотр")
async def add_view_start(message: types.Message, state: FSMContext):
    """Начать процесс добавления просмотра"""
    await state.set_state(AddRecordState.waiting_for_title)
    await message.answer(
        "🎬 Введите название фильма или сериала:",
        reply_markup=types.ReplyKeyboardRemove()
    )