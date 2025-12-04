from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_search_results_keyboard(results: list, current_page: int) -> InlineKeyboardMarkup:
    """Клавиатура для результатов поиска"""
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки для каждого результата
    for i, result in enumerate(results[current_page*5:(current_page+1)*5]):
        builder.button(
            text=f"{result['title']} ({result.get('release_year', 'N/A')})",
            callback_data=f"select_result_{result['id']}"
        )
    
    # Добавляем кнопки навигации
    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_page_{current_page-1}")
        )
    if len(results) > (current_page + 1) * 5:
        navigation_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_page_{current_page+1}")
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_search"))
    
    return builder.as_markup()