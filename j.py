import os
import django

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

# Теперь можно импортировать модели
from events_bot.models import CustomUser

# Работаем с моделью
first_user = CustomUser.objects.order_by('id').first()
first_username = first_user.username if first_user else 'Нет пользователей'

print(first_username)
