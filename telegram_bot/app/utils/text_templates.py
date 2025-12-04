from typing import List, Dict, Any

def get_start_message(username: str) -> str:
    """Шаблон приветственного сообщения"""
    return (
        f"🎬 Добро пожаловать в Movie Tracker, {username}!\n\n"
        "Здесь вы можете:\n"
        "• 📊 Вести историю просмотров\n"
        "• 📋 Создать список желаемого\n"
        "• 🔍 Искать фильмы и сериалы\n"
        "• 📈 Смотреть аналитику\n\n"
        "Выберите действие в меню ниже 👇"
    )

def get_help_message() -> str:
    """Шаблон сообщения помощи"""
    return (
        "🤖 <b>Movie Tracker Bot - Помощь</b>\n\n"
        "📝 <b>Основные команды:</b>\n"
        "/start - Начать работу\n"
        "/help - Показать эту справку\n"
        "/history - История просмотров\n"
        "/watchlist - Список желаемого\n"
        "/search - Поиск контента\n"
        "/analytics - Аналитика\n\n"
        "🎯 <b>Как использовать:</b>\n"
        "1. Добавляйте просмотренные фильмы и сериалы\n"
        "2. Оценивайте их от 1 до 10\n"
        "3. Следите за своей статистикой\n"
        "4. Планируйте будущие просмотры\n\n"
        "Для начала работы нажмите /start"
    )

def get_history_message(history: List[Dict[str, Any]]) -> str:
    """Шаблон сообщения истории"""
    if not history:
        return "📝 Ваша история просмотров пуста."
    
    message = "📊 <b>Ваша история просмотров:</b>\n\n"
    for i, record in enumerate(history[:5], 1):
        content = record.get('content', {})
        content_title = content.get('title', 'Неизвестно')
        rating = record.get('rating', 'еще нет')
        
        message += f"{i}. {content_title} - ⭐ {rating}/10\n"
    
    return message

def get_watchlist_message(watchlist: List[Dict[str, Any]]) -> str:
    """Шаблон сообщения списка желаемого"""
    if not watchlist:
        return "📝 Ваш список желаемого пуст."
    
    message = "📋 <b>Ваш список желаемого:</b>\n\n"
    for i, item in enumerate(watchlist, 1):
        content = item.get('content', {})
        content_title = content.get('title', 'Неизвестно')
        priority = item.get('priority', 1)
        
        message += f"{i}. {content_title} - Приоритет: {priority}/5\n"
    
    return message

def get_search_results_message(results: List[Dict[str, Any]], page: int) -> str:
    """Шаблон сообщения результатов поиска"""
    if not results:
        return "❌ По вашему запросу ничего не найдено."
    
    start_idx = page * 5
    end_idx = start_idx + 5
    current_results = results[start_idx:end_idx]
    
    message = f"🔍 <b>Результаты поиска</b> (стр. {page + 1}):\n\n"
    
    for i, result in enumerate(current_results, start_idx + 1):
        content_type = "фильм" if result.get('content_type') == 'movie' else "сериал"
        release_year = result.get('release_year', 'неизвестно')
        
        message += f"{i}. {result['title']} ({release_year}) - {content_type}\n"
    
    return message

def get_analytics_message(analytics: Dict[str, Any]) -> str:
    """Шаблон сообщения аналитики"""
    if not analytics:
        return "📊 Аналитика временно недоступна."
    
    total_views = analytics.get('total_views', 0)
    avg_rating = analytics.get('average_rating', 0)
    
    return (
        f"📊 <b>Ваша аналитика за последние 30 дней:</b>\n\n"
        f"🎯 Всего просмотров: {total_views}\n"
        f"⭐ Средняя оценка: {avg_rating}/10\n"
        f"📈 Активность: {'🔥 Высокая' if total_views > 10 else '📊 Средняя' if total_views > 5 else '😴 Низкая'}\n\n"
        "Для подробной статистики нажмите '📊 Статистика'"
    )

def get_settings_message() -> str:
    """Шаблон сообщения настроек"""
    return (
        "⚙️ <b>Настройки</b>\n\n"
        "Здесь вы можете настроить:\n"
        "• 🔔 Уведомления\n"
        "• 📊 Частоту отчетов\n"
        "• 🎯 Приватность\n\n"
        "Функциональность настроек находится в разработке 🚧"
    )