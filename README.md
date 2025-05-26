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


### 2. Переменные окружения
Проект использует файл `.env` для хранения конфиденциальных данных, таких как токен Telegram-бота. В репозитории уже есть шаблон `example.env`, который нужно скопировать и настроить:
1. Скопируйте файл example.env в .env:
- Для macOS и Linux выполните команду:
```bash
cp example.env .env
```
- Для Windows используйте команду:
```bash
copy example.env .env
```
2. Откройте файл `.env` в текстовом редакторе.
3. Ниже приведены переменные окружения, которые необходимо указать:

`TG_BOT_TOKEN`
- Токен Telegram-бота: укажите значение переменной `TG_BOT_TOKEN` после знака `=`:
```python
TG_BOT_TOKEN=your_telegram_bot_token
```
Чтобы получить токен, необходимо создать бота в Telegram и обратиться к [BotFather](https://telegram.me/BotFather).

`SECRET_KEY`
- Секретный ключ Django: укажите значение переменной `SECRET_KEY` после знака `=`:
```python
SECRET_KEY=your_django_token
```
Ключ можно придумать самостоятельно, используя различные символы. Это важная переменная, поэтому убедитесь, что ключ надежный.

`payment_token`
- Ключ для оплаты: укажите значение переменной `payment_token` после знака `=`:
```python
payment_token=your_payment_token
```
Ключ для оплаты, можно получить подключив оплату для бота у [BotFather](https://telegram.me/BotFather), через различные сервисы.

`organizer_chat_id`
- Чат ID организатора: укажите значение переменной `organizer_chat_id` после знака `=`:
```python
organizer_chat_id=your_organizer_chat_id
```
Чат ID организатора необходим для получения уведомлений.

Настройки проекта:\
- DEBUG=False
- ALLOWED_HOSTS=localhost,127.0.0.1
- STATIC_URL=/static/
- MEDIA_URL=/media/
- MEDIA_ROOT=media
- DATABASE_URL=postgres://meetupuser:password@db:5432/meetup


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
