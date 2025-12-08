from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.watchlist_keyboards import get_watchlist_results_keyboard
from app.keyboards.main_menu import get_main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.watchlist_service import WatchlistService
from app.states.watchlist_state import WatchlistState
from app.utils.text_templates import get_watchlist_message

router = Router()


@router.message(Command("watchlist"))
@router.message(F.text == "📋 Список желаемого")
async def cmd_watchlist(message: types.Message, state: FSMContext):
    """Показать список желаемого с пагинацией"""
    await state.clear()

    watchlist_service = WatchlistService()
    watchlist = await watchlist_service.get_user_watchlist(
        telegram_id=message.from_user.id
    )

    if not watchlist:
        await message.answer(
            "📝 Ваш список желаемого пуст.\n"
            "Добавьте первый фильм или сериал, который хотите посмотреть!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await state.update_data(watchlist_results=watchlist, watchlist_page=0)

    text = get_watchlist_message(watchlist, 0)
    keyboard = get_watchlist_results_keyboard(watchlist, 0)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(WatchlistState.viewing)


@router.callback_query(WatchlistState.viewing, F.data.startswith("watchlist_page_"))
async def change_watchlist_page(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    results = data.get("watchlist_results", [])
    if not results:
        await callback.answer("Список пуст", show_alert=True)
        return

    try:
        page = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Некорректная страница", show_alert=True)
        return

    safe_page = max(0, min(page, len(results) - 1))
    text = get_watchlist_message(results, safe_page)
    keyboard = get_watchlist_results_keyboard(results, safe_page)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(watchlist_page=safe_page)
    await callback.answer()


@router.callback_query(WatchlistState.viewing, F.data == "watchlist_clear")
async def clear_watchlist(callback: types.CallbackQuery, state: FSMContext):
    watchlist_service = WatchlistService()
    cleared = await watchlist_service.clear_watchlist(callback.from_user.id)

    if cleared:
        await state.clear()
        try:
            await callback.message.delete()
        except Exception:
            # Если сообщение удалить не удалось (например, уже удалено), продолжаем
            pass

        await callback.message.answer(
            "🗑️ Список желаемого очищен.", reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return

    await callback.answer("Не удалось очистить", show_alert=True)


@router.callback_query(WatchlistState.viewing, F.data.startswith("watchlist_add_"))
async def start_add_from_watchlist(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    results = data.get("watchlist_results", [])
    if not results:
        await callback.answer("Список пуст", show_alert=True)
        return

    try:
        page = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Некорректный выбор", show_alert=True)
        return

    if page < 0 or page >= len(results):
        await callback.answer("Элемент вне диапазона", show_alert=True)
        return

    selected = results[page]
    await state.update_data(selected_watchlist_item=selected)

    title = (selected.get("content") or {}).get("title") or selected.get("content_title") or "фильм"
    await callback.message.answer(
        f"💬 Оставьте отзыв о фильме «{title}» (или отправьте '-' чтобы пропустить):",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(WatchlistState.waiting_for_review)
    await callback.answer()


@router.message(WatchlistState.waiting_for_review)
async def watchlist_review(message: types.Message, state: FSMContext):
    review = message.text.strip()
    if review == "-":
        review = None

    await state.update_data(review=review)
    await message.answer(
        "📅 Укажите дату просмотра (в формате ДД.ММ.ГГГГ, 'сегодня' или 'вчера'):",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(WatchlistState.waiting_for_watched_at)


@router.message(WatchlistState.waiting_for_watched_at)
async def watchlist_watched_date(message: types.Message, state: FSMContext):
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
    await message.answer("⭐️ Ваша оценка от 1 до 10:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(WatchlistState.waiting_for_rating)


@router.message(WatchlistState.waiting_for_rating)
async def watchlist_rating(message: types.Message, state: FSMContext):
    try:
        rating = float(message.text.strip().replace(",", "."))
        if rating < 1 or rating > 10:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введите число от 1 до 10, например 8.5")
        return

    data = await state.get_data()
    selected = data.get("selected_watchlist_item") or {}
    watched_at = data.get("watched_at")
    review = data.get("review")

    content = (selected.get("content") or {})
    content_id = content.get("id")
    watchlist_id = selected.get("id")

    history_service = HistoryService()
    watchlist_service = WatchlistService()

    # Всегда убеждаемся, что контент существует и можем получить его ID
    ensured = await history_service.ensure_content_exists(content)
    if ensured:
        content = ensured
        content_id = content.get("id")

    if not content_id or not watchlist_id:
        await message.answer(
            "❌ Не удалось определить фильм. Попробуйте снова через список желаемого.",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    saved = await history_service.add_view_history(
        telegram_id=message.from_user.id,
        content_id=content_id,
        rating=rating,
        notes=review,
        watched_at=watched_at,
        user_profile={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    title = content.get("title") or "Фильм"

    if saved and saved.get("id"):
        await watchlist_service.remove_from_watchlist(watchlist_id)
        await message.answer(
            (
            f"✅ {title} добавлен в историю!\n"
            f"⭐️ Ваша оценка: {rating}/10\n"
            f"🗓 Дата: {watched_at.strftime('%d.%m.%Y') if isinstance(watched_at, datetime) else 'не указана'}"
            + (f"\n💬 Отзыв: {review}" if review else "")
            + "\n\nФильм удален из списка желаемого.",
            ),
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await message.answer(
            "❌ Не удалось сохранить просмотр. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(),
        )

    await state.clear()