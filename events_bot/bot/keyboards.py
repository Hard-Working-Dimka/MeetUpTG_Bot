from asgiref.sync import sync_to_async
from events_bot.models import CustomUser
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()


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

    if not user.notifications:
        builder.button(
            text='🔔 Подписаться на уведомления',
            callback_data='subscribe_notifications'
        )

    if user.role == 'organizer':
        builder.button(
            text='Отправить уведомления',
            callback_data='send_notifications'
        )

    if user.role == 'listener':
        builder.button(
            text='🎤 Подать заявку спикера',
            callback_data='apply_for_speaker'
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


def questions_keyboard(current_index: int, total_questions: int,
                       question_id: int, is_answered: bool, asker_id: str):
    builder = InlineKeyboardBuilder()

    if total_questions > 1:
        if current_index > 0:
            builder.button(
                text="← Назад", 
                callback_data=f"prev_question_{current_index-1}"
            )

        if current_index < total_questions - 1:
            builder.button(
                text="Вперед →",
                callback_data=f"next_question_{current_index+1}"
            )

    if not is_answered:
        builder.button(
            text="✏️ Ответить",
            callback_data=f"answer_question_{question_id}_{asker_id}"
        )
        builder.button(
            text="✅ Пометить как отвеченный",
            callback_data=f"mark_answered_{question_id}"
        )

    builder.adjust(2, 2)
    return builder.as_markup()


def answer_question_keyboard(asker_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✏️ Написать ответ", 
        url=f"tg://user?id={asker_id}"
    )

    return builder.as_markup()


def notifications_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Да', callback_data='confirm_subscription')
    builder.button(text='❌ Нет', callback_data='cancel_subscription')
    builder.adjust(2)

    return builder.as_markup()


def back_to_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад в меню", callback_data="main_menu")
    return builder.as_markup()
