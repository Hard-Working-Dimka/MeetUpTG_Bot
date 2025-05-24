# MeetUpTG_Bot

## Описание

Telegram-бот и веб-приложение для управления мероприятиями, анкетами, вопросами и донатами. Использует Django, aiogram и PostgreSQL.

---

## Быстрый старт (деплой через Docker)

### 1. Клонируйте репозиторий
```sh
git clone <ваш-репозиторий>
cd MeetUpTG_Bot
```

### 2. Создайте файл `.env`
Скопируйте и заполните переменные окружения:

```
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
TG_BOT_TOKEN=your_telegram_bot_token
STATIC_URL=/static/
MEDIA_URL=/media/
MEDIA_ROOT=media
DATABASE_URL=postgres://meetupuser:password@db:5432/meetup
```

### 3. Проверьте настройки Django
В файле `meetup/settings.py`:
- Должно быть:
  ```python
  STATIC_URL = env.str('STATIC_URL', default='static/')
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  # STATICFILES_DIRS = ['static']  # закомментируйте, если такой папки нет
  ```

### 4. Запустите проект
```sh
docker-compose up --build
```

- Django будет доступен на http://localhost:8000
- Бот запустится автоматически

### 5. Остановка
```sh
docker-compose down
```

---

## Полезные команды

- Создать суперпользователя:
  ```sh
  docker-compose exec web python manage.py createsuperuser
  ```
- Применить миграции вручную:
  ```sh
  docker-compose exec web python manage.py migrate
  ```
- Собрать статику вручную:
  ```sh
  docker-compose exec web python manage.py collectstatic --noinput
  ```

---

## Примечания
- Для продакшена рекомендуется настроить отдачу статики и медиа через nginx.
- Не запускайте несколько экземпляров бота с одним токеном одновременно!
- Для смены БД используйте переменную `DATABASE_URL`.

---

## Стек
- Python 3.11+
- Django 5+
- aiogram 3+
- PostgreSQL 15+
- Docker, docker-compose

---
