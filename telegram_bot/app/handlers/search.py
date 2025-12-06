# telegram_bot/app/handlers/search.py
import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.main_menu import get_main_menu_keyboard
from app.keyboards.search_keyboards import build_watch_url, get_search_results_keyboard
from app.states.search_state import SearchState
from app.utils.text_templates import get_search_results_message

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("search"))
@router.message(F.text == "🔍 Поиск")
async def cmd_search(message: types.Message, state: FSMContext):
    """Начать процесс поиска"""
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "🔍 Введите название фильма или сериала для поиска:",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(SearchState.waiting_for_query)
async def process_search_query(message: types.Message, state: FSMContext):
    """Обработать поисковый запрос"""
    query = message.text.strip()
    logger.info(f"🔍 Поиск: '{query}'")

    search_message = await message.answer("🔍 Ищем...")

    try:
        from app.services.content_service import ContentService

        content_service = ContentService()
        raw_result = await content_service.search_content(query)

        # Приводим ответ API (dict) к списку результатов для пагинации
        results = []
        error_message = None

        if isinstance(raw_result, list):
            results = raw_result
        elif isinstance(raw_result, dict):
            source = raw_result.get("source")

            # Стандартная схема API для бота
            if source in {"database", "omdb"}:
                data = raw_result.get("data")
                if isinstance(data, list):
                    results = data
                elif data:
                    results = [data]
                else:
                    error_message = raw_result.get("message")
            # Явные статусы ошибок
            elif source in {"not_found", "error"}:
                error_message = raw_result.get("message")
            # Фолбэк для произвольных структур (success/error)
            elif raw_result.get("success") is False:
                error_message = raw_result.get("error") or raw_result.get("detail")
            else:
                data = raw_result.get("data")
                if isinstance(data, list):
                    results = data
                elif data:
                    results = [data]

        if error_message:
            await search_message.edit_text(f"❌ {error_message}")
            await state.clear()
            return

        if not results:
            await search_message.edit_text("❌ Ничего не найдено. Попробуйте другой запрос.")
            await state.clear()
            return

        # ограничиваем список пятью записями
        results = results[:5]

        # Сохраняем результаты
        await state.update_data(
            search_results=results,
            current_page=0,
            search_query=query,
            total_results=len(results),
        )

        # Показываем первую страницу результатов
        text = get_search_results_message(results, 0)
        keyboard = get_search_results_keyboard(results, 0)

        await search_message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(SearchState.waiting_for_selection)
        logger.info(f"✅ Поиск завершен, найдено {len(results)} результатов")

    except Exception as e:
        logger.error(f"💥 Ошибка при поиске: {e}")
        await search_message.edit_text("❌ Произошла ошибка при поиске. Попробуйте позже.")
        await state.clear()


@router.callback_query(F.data.startswith("search_page_"))
async def change_search_page(callback: types.CallbackQuery, state: FSMContext):
    """Смена страницы результатов поиска"""
    data = await state.get_data()
    results = data.get("search_results", [])

    if not results:
        await callback.answer("Результаты не найдены", show_alert=True)
        return

    current_page = int(callback.data.split("_")[2])
    max_page = max(len(results) - 1, 0)
    current_page = max(0, min(current_page, max_page))

    text = get_search_results_message(results, current_page)
    keyboard = get_search_results_keyboard(results, current_page)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(current_page=current_page)
    await callback.answer()


@router.callback_query(F.data == "new_search")
async def new_search(callback: types.CallbackQuery, state: FSMContext):
    """Новый поиск"""
    await state.set_state(SearchState.waiting_for_query)
    await callback.message.edit_text("🔍 Введите название фильма или сериала для поиска:")
    await callback.answer()



@router.callback_query(F.data == "return_to_menu")
async def return_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🏠 Главное меню:", reply_markup=get_main_menu_keyboard()
    )