# telegram_bot/app/handlers/search.py
import logging
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.main_menu import get_main_menu_keyboard
from app.keyboards.search_keyboards import get_search_results_keyboard
from app.services.history_service import HistoryService
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


@router.callback_query(F.data.startswith("search_add_"))
async def start_add_to_history(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление выбранного результата в историю"""
    data = await state.get_data()
    results = data.get("search_results", [])

    if not results:
        await callback.answer("Результаты поиска недоступны", show_alert=True)
        return

    try:
        index = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Не удалось определить элемент", show_alert=True)
        return

    if index < 0 or index >= len(results):
        await callback.answer("Элемент вне диапазона", show_alert=True)
        return

    selected = results[index]
    title = selected.get("title") or "фильм"

    await state.update_data(selected_content=selected)
    await callback.message.answer(
        f"💬 Оставьте отзыв о фильме «{title}» (или отправьте '-' чтобы пропустить):",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(SearchState.waiting_for_review)
    await callback.answer()


@router.message(SearchState.waiting_for_review)
async def collect_review(message: types.Message, state: FSMContext):
    """Сохранить отзыв и запросить дату просмотра"""
    review = message.text.strip()
    if review == "-":
        review = None

    await state.update_data(review=review)
    await message.answer(
        "📅 Укажите дату просмотра (в формате ДД.ММ.ГГГГ, 'сегодня' или 'вчера'):",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(SearchState.waiting_for_watched_at)


@router.message(SearchState.waiting_for_watched_at)
async def collect_watched_date(message: types.Message, state: FSMContext):
    """Получить дату просмотра"""
    text = message.text.strip().lower()
    today = datetime.now()

    try:
        if text in {"сегодня", "today"}:
            watched_at = today
        elif text in {"вчера", "yesterday"}:
            watched_at = today - timedelta(days=1)
        else:
            watched_at = datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "⚠️ Не удалось распознать дату. Введите в формате ДД.ММ.ГГГГ или напишите 'сегодня'."
        )
        return

    await state.update_data(watched_at=watched_at)
    await message.answer(
        "⭐️ Ваша оценка от 1 до 10:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(SearchState.waiting_for_rating)


@router.message(SearchState.waiting_for_rating)
async def collect_rating(message: types.Message, state: FSMContext):
    """Получить оценку, сохранить историю и завершить"""
    try:
        rating = float(message.text.strip().replace(",", "."))
        if rating < 1 or rating > 10:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введите число от 1 до 10, например 8.5")
        return

    data = await state.get_data()
    selected = data.get("selected_content")
    watched_at = data.get("watched_at")
    review = data.get("review")

    if not selected:
        await message.answer("❌ Не удалось найти данные выбранного фильма. Попробуйте поиск снова.")
        await state.clear()
        return

    history_service = HistoryService()

    content = await history_service.ensure_content_exists(selected)
    if not content or not content.get("id"):
        await message.answer(
            "❌ Не удалось подготовить фильм для сохранения. Попробуйте позже или сделайте новый поиск."
        )
        await state.clear()
        return

    saved = await history_service.add_view_history(
        telegram_id=message.from_user.id,
        content_id=content["id"],
        rating=rating,
        notes=review,
        watched_at=watched_at,
        user_profile={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    title = content.get("title") or selected.get("title") or "Фильм"

    if saved and saved.get("id"):
        await message.answer(
            (
                f"✅ {title} добавлен в историю!\n"
                f"⭐️ Ваша оценка: {rating}/10\n"
                f"🗓 Дата: {watched_at.strftime('%d.%m.%Y') if isinstance(watched_at, datetime) else 'не указана'}"
                + (f"\n💬 Отзыв: {review}" if review else "")
            ),
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await message.answer(
            "❌ Не удалось сохранить просмотр. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(),
        )

    await state.clear()


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
    await callback.answer()


@router.callback_query(F.data.startswith("search_watchlist_"))
async def add_to_watchlist(callback: types.CallbackQuery, state: FSMContext):
    """Быстро добавить найденный фильм в список желаемого/историю"""
    data = await state.get_data()
    results = data.get("search_results", [])

    if not results:
        await callback.answer("Результаты недоступны", show_alert=True)
        return

    try:
        index = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Не удалось определить элемент", show_alert=True)
        return

    if index < 0 or index >= len(results):
        await callback.answer("Элемент вне диапазона", show_alert=True)
        return

    selected = results[index]
    history_service = HistoryService()

    content = await history_service.ensure_content_exists(selected)
    if not content or not content.get("id"):
        await callback.answer("Не удалось подготовить фильм", show_alert=True)
        return

    saved = await history_service.add_view_history(
        telegram_id=callback.from_user.id,
        content_id=content["id"],
        notes="Добавлено в watchlist",
        user_profile={
            "username": callback.from_user.username,
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
        },
    )

    if saved and saved.get("id"):
        await callback.answer("✅ Добавлено в watchlist")
    else:
        await callback.answer("Не удалось добавить", show_alert=True)
