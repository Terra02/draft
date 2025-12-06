import os
from urllib.parse import quote_plus

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

__all__ = ["get_search_results_keyboard", "build_watch_url"]

OMDB_API_URL = os.getenv("OMDB_API_URL", "https://www.omdbapi.com/")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def build_watch_url(result: dict) -> str:
    imdb_id = result.get("imdb_id")
    title = result.get("title", "")
    release_year = result.get("release_year")

    if imdb_id:
        base = OMDB_API_URL.rstrip("/") + "/"
        query = f"i={quote_plus(imdb_id)}"
        if OMDB_API_KEY:
            query = f"{query}&apikey={quote_plus(OMDB_API_KEY)}"
        return f"{base}?{query}"

    query = title
    if release_year:
        query = f"{title} {release_year}"

    return f"https://www.google.com/search?q={quote_plus(query)}"


def get_search_results_keyboard(results: list, current_page: int) -> InlineKeyboardMarkup:
    """Клавиатура для результатов поиска"""
    builder = InlineKeyboardBuilder()
    if not results:
        builder.button(text="🔍 Новый поиск", callback_data="new_search")
        builder.button(text="🏠 Меню", callback_data="return_to_menu")
        builder.adjust(1)
        return builder.as_markup()

    safe_page = max(0, min(current_page, len(results) - 1))
    current = results[safe_page]

    # Добавляем кнопки навигации
    navigation_buttons = []
    if safe_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_page_{safe_page-1}")
        )
    if safe_page < len(results) - 1:
        navigation_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_page_{safe_page+1}")
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    

    # Кнопки дополнительных действий
    builder.row(
        InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="return_to_menu"),
    )

    
    return builder.as_markup()