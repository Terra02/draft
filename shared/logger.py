"""
Общая настройка логирования для всех сервисов
"""

import logging
import sys
import json
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Форматтер для JSON логов"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging(level: int = logging.INFO, json_format: bool = False):
    """
    Настройка логирования для всех сервисов
    
    Args:
        level: Уровень логирования
        json_format: Использовать JSON формат
    """
    # Создаем форматтер
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Обработчик для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=level,
        handlers=[handler]
    )
    
    # Устанавливаем уровень для сторонних библиотек
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)