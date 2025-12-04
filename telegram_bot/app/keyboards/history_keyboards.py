from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_history_navigation_keyboard(current_index: int, total: int, record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по истории"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    if current_index > 0:
        builder.button(text="⬅️", callback_data=f"history_prev_{current_index-1}")
    
    builder.button(text=f"{current_index + 1}/{total}", callback_data="current_page")
    
    if current_index < total - 1:
        builder.button(text="➡️", callback_data=f"history_next_{current_index+1}")
    
    builder.row()
    builder.button(text="⭐ Оценить", callback_data=f"rate_{record_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"edit_{record_id}")
    
    builder.row()
    builder.button(text="❌ Удалить", callback_data=f"delete_{record_id}")
    builder.button(text="📋 В меню", callback_data="main_menu")
    
    return builder.as_markup()

def get_rating_keyboard(record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для оценки"""
    builder = InlineKeyboardBuilder()
    
    for i in range(1, 11):
        builder.button(text=str(i), callback_data=f"set_rating_{record_id}_{i}")
    
    builder.row()
    builder.button(text="↩️ Назад", callback_data="back_to_history")
    
    return builder.as_markup()