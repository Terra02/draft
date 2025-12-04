from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_rating_keyboard(record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для оценки контента"""
    builder = InlineKeyboardBuilder()
    
    # Создаем кнопки с оценками от 1 до 10
    for i in range(1, 6):
        builder.button(text=str(i), callback_data=f"rating_{record_id}_{i}")
    builder.row()
    for i in range(6, 11):
        builder.button(text=str(i), callback_data=f"rating_{record_id}_{i}")
    
    builder.row()
    builder.button(text="↩️ Назад", callback_data="back_to_details")
    
    return builder.as_markup()