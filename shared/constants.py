"""
Общие константы приложения
"""

# Типы контента
CONTENT_TYPE_MOVIE = "movie"
CONTENT_TYPE_SERIES = "series"
CONTENT_TYPES = [CONTENT_TYPE_MOVIE, CONTENT_TYPE_SERIES]

# Максимальные длины полей
MAX_TITLE_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 2000
MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 255
MAX_NOTES_LENGTH = 1000

# Валидация рейтингов
MIN_RATING = 1
MAX_RATING = 10

# Приоритеты watchlist
MIN_PRIORITY = 1
MAX_PRIORITY = 5

# Пагинация
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Время кэширования (в секундах)
CACHE_TTL = 300  # 5 минут

# Статусы
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"