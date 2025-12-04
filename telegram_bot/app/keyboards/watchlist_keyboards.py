from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_watchlist_keyboard(watchlist: list) -> InlineKeyboardMarkup:
    """Клавиатура для списка желаемого"""
    builder = InlineKeyboardBuilder()
    
    for item in watchlist:
        builder.button(
            text=f"🎬 {item['content_title']}",
            callback_data=f"watchlist_detail_{item['id']}"
        )
    
    builder.row()
    builder.button(text="➕ Добавить", callback_data="add_to_watchlist")
    builder.button(text="🗑️ Очистить", callback_data="clear_watchlist")
    
    builder.row()
    builder.button(text="📋 В меню", callback_data="main_menu")
    
    return builder.as_markup()