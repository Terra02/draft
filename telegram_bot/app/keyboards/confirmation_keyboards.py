from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения действия"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="✅ Да",
        callback_data=f"confirm_{action}_{item_id}"
    )
    builder.button(
        text="❌ Нет", 
        callback_data=f"cancel_{action}_{item_id}"
    )
    
    return builder.as_markup()