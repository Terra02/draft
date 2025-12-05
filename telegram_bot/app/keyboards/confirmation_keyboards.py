# app/keyboards/confirm_keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Да, всё верно", callback_data="confirm_yes")
    builder.button(text="✏️ Нет, исправить", callback_data="confirm_no")
    
    builder.adjust(1)
    return builder.as_markup()