import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Настройка логирования для воркера"""
    # Создаем директорию для логов если не существует
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для файла
    file_handler = RotatingFileHandler(
        f"{log_dir}/worker.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Уменьшаем логировние для некоторых библиотек
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)