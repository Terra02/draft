"""
Общие исключения приложения
"""

class MovieTrackerException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class DatabaseException(MovieTrackerException):
    """Исключение базы данных"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, "DATABASE_ERROR")

class APIClientException(MovieTrackerException):
    """Исключение клиента API"""
    def __init__(self, message: str = "API client error occurred"):
        super().__init__(message, "API_CLIENT_ERROR")

class ValidationException(MovieTrackerException):
    """Исключение валидации"""
    def __init__(self, message: str = "Validation error occurred"):
        super().__init__(message, "VALIDATION_ERROR")

class NotFoundException(MovieTrackerException):
    """Исключение - не найдено"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")

class ExternalServiceException(MovieTrackerException):
    """Исключение внешнего сервиса"""
    def __init__(self, message: str = "External service error occurred"):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")