from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from app.keyboards.watchlist_keyboards import get_watchlist_keyboard
from app.keyboards.main_menu import get_main_menu_keyboard
from app.services.watchlist_service import WatchlistService
from app.utils.text_templates import get_watchlist_message

router = Router()

@router.message(Command("watchlist"))
@router.message(F.text == "📋 Список желаемого")
async def cmd_watchlist(message: types.Message, state: FSMContext):
    """Показать список желаемого"""
    await state.clear()

    watchlist_service = WatchlistService()
    watchlist = await watchlist_service.get_user_watchlist(
        telegram_id=message.from_user.id
    )

    if not watchlist:
        await message.answer(
            "📝 Ваш список желаемого пуст.\n"
            "Добавьте первый фильм или сериал, который хотите посмотреть!",
            reply_markup=get_main_menu_keyboard()
        )
        return

    text = get_watchlist_message(watchlist)
    keyboard = get_watchlist_keyboard(watchlist)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("watchlist_remove_"))
async def remove_from_watchlist(callback: types.CallbackQuery):
    """Удалить из списка желаемого"""
    item_id = int(callback.data.split("_")[2])
    
    watchlist_service = WatchlistService()
    success = await watchlist_service.remove_from_watchlist(item_id)
    
    if success:
        await callback.answer("Удалено из списка желаемого")
        # Обновляем сообщение
        await cmd_watchlist(callback.message, callback.message.bot)
    else:
        await callback.answer("Ошибка при удалении")