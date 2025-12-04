FROM python:3.11-slim

WORKDIR /app
#RUN - выполняет команду в процессе сборки образа
#apt-get update - обновляет список доступных пакетов (обязательно делать перед установкой)
#apt-get install -y - устанавливает пакеты:
#gcc - компилятор C (нужен для компиляции некоторых Python-пакетов)
#libpq-dev - библиотеки для работы с PostgreSQL (если используете psycopg2)
#&& - оператор "И" (следующая команда выполнится только если предыдущая успешна)
#rm -rf /var/lib/apt/lists/* - удаляет кэш пакетов, уменьшая размер итогового образа

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .
#убрал --no-cache чтобы ускорить сборку
RUN pip install  --upgrade pip && \
    pip install  -r requirements.txt

COPY . .
#этот порт слушает контейнер
EXPOSE 8000

#набор аргументов по умолчанию
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 

#uvicorn - ASGI-сервер для Python
#app.main:app - указывает на приложение:
#app.main - модуль main.py в пакете app
#app - переменная с экземпляром приложения внутри модуля (обычно app = FastAPI())
#--host 0.0.0.0 - сервер слушает все сетевые интерфейсы (доступен извне контейнера)
#--port 8000 - порт для прослушивания
#--reload - автоматическая перезагрузка при изменении кода (только для разработки!)
