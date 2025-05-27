import os
import sys
import django
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()


from datetime import datetime
from keyboards import main_keyboard, questions_keyboard
from django.utils import timezone
from aiogram import types
from asgiref.sync import sync_to_async
from events_bot.models import Event
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext




@sync_to_async
def get_events():
    now = datetime.now()
    return {
        'current': list(Event.objects.filter(start_at__lte=now)),
        'upcoming': list(Event.objects.filter(start_at__gt=now).order_by('start_at'))
    }


async def show_events(message: types.Message, user_id: int):
    now = timezone.now()
    events = await sync_to_async(
        lambda: {
            'current': list(Event.objects.filter(start_at__lte=now, end_at__gte=now)),
            'upcoming': list(Event.objects.filter(start_at__gt=now).order_by('start_at'))
        }
    )()

    if events['current']:
        text = 'Сейчас проходит:\n'
        for event in events['current']:
            text += f"{event.name} (начало: {event.start_at.strftime('%d.%m.%Y %H:%M')})"
    else:
        text = 'Сейчас нет активных мероприятий.\n'

    if events['upcoming']:
        text += '\n\nБлижайшие мероприятия:\n'
        for event in events['upcoming']:
            text += f"{event.name} ({event.start_at.strftime('%d.%m.%Y %H:%M')})"
    else:
        text += '\nБудущих мероприятий не запланировано.'

    add_text = '\n\nВыберите дальнейшие действия:'
    await message.answer(f'{text}{add_text}', reply_markup=await main_keyboard(user_id))


async def display_question(callback: CallbackQuery, state: FSMContext, index: int):
    data = await state.get_data()
    questions = data['questions']

    if index < 0 or index >= len(questions):
        await callback.answer("Нет больше вопросов")
        return

    question = questions[index]
    asker = question.asker

    message_text = (
        f"Вопрос {index + 1} из {len(questions)}\n\n"
        f"Событие: {question.event.name}\n"
        f"Тема: {question.presentation.topic}\n"
        f"От: {asker.full_name or asker.username or 'Аноним'}\n"
        f"Вопрос: {question.question_text}\n\n"
        f"Статус: {'✅ Отвечено' if question.answered else '❌ Не отвечено'}"
    )

    keyboard = questions_keyboard(
        current_index=index,
        total_questions=len(questions),
        question_id=question.id,
        is_answered=question.answered,
        asker_id=asker.telegram_id
    )
    try:
        await callback.message.edit_text(
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except:
        await callback.message.answer(
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    await state.update_data(current_unanswered_index=index)