from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.history_keyboards import get_history_results_keyboard, get_rating_keyboard
from app.keyboards.main_menu import get_main_menu_keyboard
from app.services.history_service import HistoryService
from app.states.history_state import HistoryState
from app.utils.formatters import format_history_record
from app.utils.text_templates import get_history_results_message

router = Router()

@router.message(Command("history"))
@router.message(F.text == "📊 История просмотров")
async def cmd_history(message: types.Message, state: FSMContext):
    """Показать историю просмотров"""
    await state.clear()

    history_service = HistoryService()
    history = await history_service.get_user_history(
        telegram_id=message.from_user.id,
        limit=50,
        profile={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    if not history:
        await message.answer(
            "📝 Ваша история просмотров пуста.\n"
            "Добавьте первый просмотренный фильм или сериал!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await state.update_data(history_records=history, history_page=0)
    await state.set_state(HistoryState.viewing)

    text = get_history_results_message(history, 0)
    keyboard = get_history_results_keyboard(history, 0)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("history_page_"))
async def paginate_history(callback: types.CallbackQuery, state: FSMContext):
    """Переключение между элементами истории"""
    data = await state.get_data()
    history = data.get("history_records", [])

    if not history:
        await callback.answer("История недоступна", show_alert=True)
        return

    try:
        page = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.answer("Некорректная страница", show_alert=True)
        return

    safe_page = max(0, min(page, len(history) - 1))

    text = get_history_results_message(history, safe_page)
    keyboard = get_history_results_keyboard(history, safe_page)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(history_page=safe_page)
    await callback.answer()


@router.callback_query(F.data == "history_page_current")
async def history_page_current(callback: types.CallbackQuery):
    """Заглушка для кнопки текущей страницы"""
    await callback.answer()

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
