from typing import Dict, Any, List
from datetime import datetime

def format_history_record(record: Dict[str, Any]) -> str:
    """Форматирование записи истории"""
    content = record.get('content', {})
    content_title = content.get('title', 'Неизвестно')
    content_type = "фильм" if content.get('content_type') == 'movie' else "сериал"
    
    watched_at = record.get('watched_at', '')
    if watched_at:
        watched_at = datetime.fromisoformat(watched_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
    
    rating = record.get('rating')
    rating_text = f"⭐ Оценка: {rating}/10" if rating else "⭐ Оценка: не указана"
    
    notes = record.get('notes', '')
    notes_text = f"\n📝 Заметки: {notes}" if notes else ""
    
    return (
        f"🎬 {content_title}\n"
        f"📁 Тип: {content_type}\n"
        f"📅 Просмотрено: {watched_at}\n"
        f"{rating_text}{notes_text}"
    )

def format_analytics_message(stats: Dict[str, Any]) -> str:
    """Форматирование сообщения аналитики"""
    total_views = stats.get('total_views', 0)
    movies_views = stats.get('movies_views', 0)
    series_views = stats.get('series_views', 0)
    avg_rating = stats.get('average_rating', 0)
    
    return (
        f"📊 Ваша статистика:\n\n"
        f"🎯 Всего просмотров: {total_views}\n"
        f"🎬 Фильмов: {movies_views}\n"
        f"📺 Сериалов: {series_views}\n"
        f"⭐ Средняя оценка: {avg_rating}/10\n"
    )