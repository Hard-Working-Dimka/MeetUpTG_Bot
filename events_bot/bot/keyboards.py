import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()


from aiogram.utils.keyboard import InlineKeyboardBuilder
from events_bot.models import CustomUser
from asgiref.sync import sync_to_async


def start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Посмотреть мероприятия',
        callback_data='show_events'
    )
    return builder.as_markup()


async def main_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=user_id)

    builder.button(
        text='❔ Задать вопрос докладчику',
        callback_data='ask_speaker'
    )

    builder.button(
        text='📅 Программа мероприятия',
        callback_data='show_schedule'
    )

    builder.button(
        text='💬 Пообщаться с разработчиками',
        callback_data='connect_devs'
    )

    builder.button(
        text='💵 Поддержать организаторов',
        callback_data='donate'
    )

    if user.role == 'speaker':
        builder.button(
            text='Мои вопросы',
            callback_data='show_my_questions'
        )

    builder.adjust(1)
    return builder.as_markup()


def show_speakers(speakers):
    builder = InlineKeyboardBuilder()
    for speaker in speakers:
        presentations = speaker.presentation_set.all()

        speaker_name = f'{speaker.first_name} {speaker.last_name}'

        if presentations:
            topics = ", ".join([p.topic for p in presentations])
            button_text = f'{speaker_name} ({topics})'
        else:
            button_text = f'{speaker_name} (нет тем)'

        if speaker.is_active:
            button_text += ' ✅'
        else:
            button_text += ' ❌'

        builder.button(
            text=button_text,
            callback_data=f'speaker_{speaker.id}'
        )
    builder.adjust(1)
    return builder.as_markup()


def speaker_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Показать мои вопросы",
        callback_data="show_my_questions"
    )

    builder.adjust(1)
    return builder.as_markup()


def profiles_keyboard(page: int, total_pages: int):
    builder = InlineKeyboardBuilder()

    if page == 0 and total_pages > 1:
        builder.button(text="Вперед →", callback_data=f"next_page_{page+1}")

    elif page == total_pages - 1 and total_pages > 1:
        builder.button(text="← Назад", callback_data=f"prev_page_{page-1}")

    elif 0 < page < total_pages - 1:
        builder.button(text="← Назад", callback_data=f"prev_page_{page-1}")
        builder.button(text="Вперед →", callback_data=f"next_page_{page+1}")

    else:
        return None

    builder.adjust(2)
    return builder.as_markup()


def questions_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Ответить на вопрос",
        callback_data="answer_question"
    )
    builder.button(
        text="✅ Пометить как отвеченный",
        callback_data="mark_answered"
    )
    builder.adjust(1)
    return builder.as_markup()