import os
import sys
import django
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()


from datetime import datetime
from keyboards import main_keyboard

from aiogram import types
from asgiref.sync import sync_to_async
from events_bot.models import Event




@sync_to_async
def get_events():
    now = datetime.now()
    return {
        'current': list(Event.objects.filter(start_at__lte=now)),
        'upcoming': list(Event.objects.filter(start_at__gt=now).order_by('start_at'))
    }


async def show_events(message: types.Message, user_id: int):
    events = await get_events()
    current_events = events['current']
    upcoming_events = events['upcoming']

    if current_events:
        text = 'Сейчас проходит:\n'
        for event in current_events:
            text += f"\n{event.name} (начало: {event.start_at.strftime('%d.%m.%Y %H:%M')})"
    else:
        text = 'Сейчас нет активных мероприятий.\n'

    if upcoming_events:
        text += '\n\nБлижайшие мероприятия:\n'
        for event in upcoming_events:
            text += f"\n{event.name} ({event.start_at.strftime('%d.%m.%Y %H:%M')})"
    else:
        text += '\nБудущих мероприятий не запланировано.'

    add_text = '\n\nВыберите дальнейшие действия:'
    await message.answer(f'{text}{add_text}', reply_markup=await main_keyboard(user_id))