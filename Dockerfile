# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Переменные окружения для Django
ENV PYTHONUNBUFFERED=1

# Команда по умолчанию (можно переопределить в docker-compose)
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python events_bot/bot/run_bot.py"] 