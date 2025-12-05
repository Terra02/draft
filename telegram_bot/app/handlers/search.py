# telegram_bot/app/handlers/search.py
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.states.search_state import SearchState
from app.keyboards.search_keyboards import get_search_results_keyboard
from app.utils.text_templates import get_search_results_message
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("search"))
@router.message(F.text == "🔍 Поиск")
async def cmd_search(message: types.Message, state: FSMContext):
    """Начать процесс поиска"""
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "🔍 Введите название фильма или сериала для поиска:",
        reply_markup=types.ReplyKeyboardRemove()
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
        results = await content_service.search_content(query)
        
        if not results:
            await search_message.edit_text("❌ Ничего не найдено. Попробуйте другой запрос.")
            await state.clear()
            return
        
        # Сохраняем результаты
        await state.update_data(
            search_results=results,
            current_page=0,
            search_query=query,
            total_results=len(results)
        )
        
        # Показываем первую страницу результатов
        text = get_search_results_message(results, 0)
        keyboard = get_search_results_keyboard(results, 0)
        
        await search_message.edit_text(text, reply_markup=keyboard)
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
    current_page = int(callback.data.split("_")[2])
    
    text = get_search_results_message(results, current_page)
    keyboard = get_search_results_keyboard(results, current_page)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.update_data(current_page=current_page)
    await callback.answer()

@router.callback_query(F.data == "new_search")
async def new_search(callback: types.CallbackQuery, state: FSMContext):
    """Новый поиск"""
    await state.set_state(SearchState.waiting_for_query)
    await callback.message.edit_text("🔍 Введите название фильма или сериала для поиска:")
    await callback.answer()