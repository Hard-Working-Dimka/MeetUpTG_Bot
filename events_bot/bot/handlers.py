import os
import sys
import django
from typing import Dict
from django.utils import timezone
from datetime import timezone as dt_timezone
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

from textwrap import dedent
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asgiref.sync import sync_to_async
from aiogram.types import LabeledPrice, PreCheckoutQuery

from events_bot.models import (
    CustomUser,
    Question,
    Presentation,
    Event,
    Donation,
    SpeakerApplication
)
from utils import show_events
from keyboards import (
    start_keyboard,
    show_speakers,
    profiles_keyboard,
    questions_keyboard,
    notifications_keyboard,
    main_keyboard
)

router = Router()


class Form(StatesGroup):
    asking_question = State()
    answering_question = State()


class ProfileStates(StatesGroup):
    waiting_about = State()
    waiting_stack = State()
    waiting_grade = State()
    waiting_full_name = State()
    waiting_phone = State()


class PaymentStates(StatesGroup):
    waiting_amount = State()
    confirming_payment = State()


class NotificationStates(StatesGroup):
    confirming_subscription = State()


class SpeakerApplicationStates(StatesGroup):
    waiting_for_topic = State()
    waiting_for_description = State()
    waiting_for_experience = State()


load_dotenv()


@router.message(Command('start'))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        user_info = await sync_to_async(CustomUser.objects.get)(telegram_id=user_id)
        role = user_info.role
        text = {
            'organizer': 'Добро пожаловать, организатор!',
            'speaker': 'Добро пожаловать, докладчик!',
            'listener': 'Добро пожаловать, пользователь!'
        }.get(role, 'Добро пожаловать!')
    except CustomUser .DoesNotExist:
        new_user = CustomUser(telegram_id=user_id, username=username, role='listener')
        await sync_to_async(new_user.save)()

        text = dedent("""
            Привет! Вижу вы новый пользователь.
            Подробнее узнать о боте можно командой /help.
            Твоя роль — пользователь.
            Для смены роли обратитесь к [организатору](https://t.me/STARKAS93) 
        """)

    await message.answer(
        text,
        parse_mode='Markdown',
        reply_markup=start_keyboard()
    )


@router.message(Command('help'))
async def help_handler(message: types.Message):
    text = dedent("""
                    *Привет! Я — бот мероприятия. Вот что я умею:*
                    *Для обычных пользователей:*
                    • Найти и задать вопрос докладчику текущего или любого выступления
                    • Получить актуальную программу мероприятия
                    • Познакомиться с другими участниками через анкету и обмен контактами
                    • Задать вопрос заказчику или сменить собеседника при общении
                    • Поддержать организаторов донатом

                    *Для докладчиков:*
                    — Получать вопросы от аудитории и видеть контакты слушателей

                    *Для организаторов:*
                    — Управлять списком докладчиков и программой
                    — Оповещать участников рассылками
                    — Видеть список донатов и суммы

                  Перейти к основному функционалу бота /start
                """)
    await message.answer(text, parse_mode='Markdown')


@router.callback_query(F.data == 'show_events')
async def handle_events_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    await show_events(callback.message, user_id)
    await callback.answer()


@router.callback_query(F.data == 'ask_speaker')
async def ask_speaker(callback: CallbackQuery):
    speakers = await sync_to_async(list)(
        CustomUser.objects.filter(role='speaker')
        .prefetch_related('presentation_set')
    )
    markup = show_speakers(speakers)
    text = dedent("""
                  ✅ - Докладчик сейчас выступает
                  ❌ - Докладчик ещё не выступал или уже выступил
                  (Тема выступления указана в скобках)
                  Выберите докладчика:
            """)
    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith('speaker_'))
async def input_question(callback: CallbackQuery, state: FSMContext):
    speaker_id = int(callback.data.split('_')[1])
    speaker = await sync_to_async(
        lambda: CustomUser.objects
        .prefetch_related('presentation_set')
        .get(id=speaker_id)
    )()

    active_presentation = next(
        (p for p in speaker.presentation_set.all() if p.is_active), 
        None
    )

    await state.update_data({
        'selected_speaker_id': speaker_id,
        'presentation_id': active_presentation.id if active_presentation else None
    })

    speaker_name = f'{speaker.first_name} {speaker.last_name}'

    await callback.message.edit_text(
        f'Введите ваш вопрос для {speaker_name}'
    )
    await state.set_state(Form.asking_question)
    await callback.answer()


@router.message(Form.asking_question)
async def process_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    speaker_id = data.get("selected_speaker_id")
    presentation_id = data.get('presentation_id')
    question_text = message.text.strip()

    question = await sync_to_async(Question.objects.create)(
        presentation_id=presentation_id,
        question_text=question_text,
        answered=False
    )

    speaker = await sync_to_async(CustomUser.objects.get)(id=speaker_id)

    speaker_name = f'{speaker.first_name} {speaker.last_name}'

    await message.answer(
        f'Ваш вопрос \"{question_text}\" отправлен докладчику: {speaker_name}.'
    )

    await state.clear()


@router.callback_query(F.data == 'show_my_questions')
async def show_my_questions(callback: CallbackQuery):

    speaker = await sync_to_async(CustomUser.objects.get)(
        telegram_id=callback.from_user.id
    )

    questions = await sync_to_async(list)(
            Question.objects.filter(presentation__user=speaker)
            .select_related('presentation', 'presentation__user')
            .order_by('-presentation__start_at')
        )

    if not questions:
        await callback.message.answer("Вам пока не задавали вопросов.")
        return await callback.answer()


    bot_message = ["Вопросы к вашим выступлениям:\n"]
    for question in questions[:10]:
        presenter = question.presentation.user
        asker_name = f"@{presenter.telegram_name}" if presenter.telegram_name else "Аноним"

        bot_message.append(
                f"Тема: <b>{question.presentation.topic}</b>\n"
                f"От: {asker_name}\n"
                f"Вопрос: {question.question_text}\n"
                f"Дата: {question.presentation.start_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"Статус: {'✅ Отвечено' if question.answered else '❌ Не отвечено'}\n"
                "──────────────────"
            )

    await callback.message.answer(
            "\n".join(bot_message),
            parse_mode="HTML",
            reply_markup=questions_keyboard(),
            disable_web_page_preview=True
        )
    await callback.answer()


@router.callback_query(F.data == 'show_schedule')
async def show_event_schedule(callback: CallbackQuery):
    now = timezone.now()
    event = await sync_to_async(
        lambda: Event.objects.filter(
            start_at__lte=now
        ).order_by('start_at').first()
    )()

    if not event:
        await callback.message.answer("На данный момент нет запланированных мероприятий")
        return await callback.answer()

    presentations = await sync_to_async(list)(
        Presentation.objects.filter(event=event)
        .select_related('user')
        .order_by('start_at')
    )

    event_info = (
        f"<b>{event.name}</b>\n"
        f"{event.start_at.strftime('%d.%m.%Y с %H:%M')}\n"
        f"\n<b>Программа:</b>\n"
    )

    schedule = []
    if not presentations:
        schedule.append("\nПока нет запланированных выступлений")
    else:
        for presentation in presentations:
            start_time = presentation.start_at.strftime('%H:%M')
            end_time = presentation.end_at.strftime('%H:%M')
            time_range = f"с {start_time} до {end_time}"
            speaker_name = f'{presentation.user.first_name} {presentation.user.last_name}'
            schedule.append(
                f'\nТема доклада: "{presentation.topic}"\n'
                f'Докладчик: {speaker_name}\n'
                f'Время проведения: {time_range}\n'
            )

    full_text = event_info + "\n".join(schedule)

    await callback.message.answer(full_text, parse_mode='HTML')
    await callback.answer()


user_pagination: Dict[int, int] = {}


@router.callback_query(F.data == 'connect_devs')
async def connect_developers(callback: CallbackQuery, state: FSMContext):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)

    required_fields = [
        ('full_name', 'Пожалуйста, укажите ваше ФИО:'),
        ('phone_number', 'Укажите ваш номер телефона (+79991234567):'),
        ('about_user', 'Напишите краткое описание о себе (чем занимаетесь, интересы):')
    ]

    for field, message_text in required_fields:
        if not getattr(user, field):
            await callback.message.answer(message_text)
            await state.set_state(getattr(ProfileStates, f'waiting_{field}'))
            return await callback.answer()

    await show_profiles(callback.message, user)
    await callback.answer()


@router.message(ProfileStates.waiting_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("ФИО должно содержать минимум 5 символов. Попробуйте еще раз:")
        return

    await state.update_data(full_name=message.text)

    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)
    if not user.phone_number:
        await message.answer("Укажите ваш номер телефона (+79991234567):")
        await state.set_state(ProfileStates.waiting_phone)
    else:
        await message.answer("Напишите краткое описание о себе (чем занимаетесь, интересы):")
        await state.set_state(ProfileStates.waiting_about)


@router.message(ProfileStates.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        phone = message.text.strip()
        if not phone.startswith('+'):
            phone = f'+7{phone[-10:]}'

        await state.update_data(phone_number=phone)

        await message.answer("Напишите краткое описание о себе:")
        await state.set_state(ProfileStates.waiting_about)

    except Exception as e:
        await message.answer("Неверный формат номера. Пожалуйста, укажите номер в формате +79991234567:")


@router.message(ProfileStates.waiting_about)
async def process_about(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await message.answer(
        'Какие языки программирования и библиотеками вы пользуетесь? (ваш стек):'
    )
    await state.set_state(ProfileStates.waiting_stack)


@router.message(ProfileStates.waiting_stack)
async def process_stack(message: types.Message, state: FSMContext):
    await state.update_data(stack=message.text)
    await message.answer('Ваш уровень опыта (Junior, Middle, Senior и т.д.):')
    await state.set_state(ProfileStates.waiting_grade)


@router.message(ProfileStates.waiting_grade)
async def process_grade(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)

    user.full_name = data.get('full_name', user.full_name)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.about_user = data['about']
    user.stack = data['stack']
    user.grade = message.text

    await sync_to_async(user.save)()

    await message.answer("✅ Ваша анкета успешно сохранена!")
    await state.clear()

    await show_profiles(message, user)


async def show_profiles(message: types.Message, current_user, page: int = 0):
    per_page = 1

    users = await sync_to_async(list)(
        CustomUser.objects.exclude(id=current_user.id)
        .filter(
            full_name__isnull=False,
            phone_number__isnull=False,
            about_user__isnull=False,
            stack__isnull=False,
            grade__isnull=False
        )
        .order_by('?')
    )

    if not users:
        await message.answer("Пока нет других анкет для просмотра.")
        return

    total_pages = (len(users) // per_page) + (1 if len(users) % per_page else 0)

    user_pagination[message.from_user.id] = page

    start = page * per_page
    end = start + per_page
    users_page = users[start:end]

    message_text = "Доступные анкеты:\n\n"

    for user in users_page:
        message_text += (
            f'ФИО: <b>{user.full_name}</b>\n'
            f'Телефон: <b>{user.phone_number}</b>\n'
            f"О себе: {user.about_user}\n"
            f"Стек: {user.stack}\n"
            f"Уровень: {user.grade}\n"
        )

        if user.username:
            message_text += f"💬 Telegram: https://t.me/{user.username}\n"

    await message.answer(
        message_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=profiles_keyboard(page, total_pages)
    )


@router.callback_query(F.data.startswith(("prev_page_", "next_page_")))
async def handle_pagination(callback: CallbackQuery):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    page = int(callback.data.split("_")[-1])

    await callback.message.delete()
    await show_profiles(callback.message, user, page)
    await callback.answer()


@router.callback_query(F.data == 'donate')
async def get_summ_donate(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите сумму доната в рублях:')
    await state.set_state(PaymentStates.waiting_amount)
    await callback.answer()


@router.message(PaymentStates.waiting_amount)
async def donate(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(
            amount=amount,
            user_id=message.from_user.id
        )

        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="Поддержка организаторов",
            description=f"Донат на сумму {amount} руб.",
            payload="donation",
            provider_token=os.environ['payment_token'],
            currency="RUB",
            prices=[LabeledPrice(label="Донат", amount=int(amount * 100))],
            start_parameter="donation"
        )
        await state.set_state(PaymentStates.confirming_payment)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")
        return


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@router.message(F.successful_payment, PaymentStates.confirming_payment)
async def process_successful_payment(message: types.Message, state: FSMContext):
    payment = message.successful_payment
    data = await state.get_data()

    user = await sync_to_async(CustomUser.objects.get)(telegram_id=data['user_id'])
    await sync_to_async(Donation.objects.create)(
        user=user,
        summ=payment.total_amount / 100
    )

    await message.answer(
        f"Спасибо за ваш донат {payment.total_amount / 100} руб.! "
        "\nСредства пойдут на организацию мероприятий."
    )
    await state.clear()


@router.message(Command('cancel'), StateFilter('*'))
async def cancel_payment(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операция отменена. Вы можете начать заново.")


@router.callback_query(F.data == 'subscribe_notifications')
async def ask_subscription(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        "Хотите получать уведомления об изменениях программы,\n"
        "времени начала, спикерах и других важных обновлениях?",
        reply_markup=notifications_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == 'confirm_subscription')
async def confirm_subscription(callback: CallbackQuery):
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=callback.from_user.id)
    user.notifications = True
    await sync_to_async(user.save)()

    await callback.message.edit_text("✅ Вы подписались на уведомления!")
    await callback.answer()


@router.callback_query(F.data == 'cancel_subscription')
async def cancel_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id

    await callback.message.edit_text(
        "Вы можете подписаться на уведомления позже.",
        reply_markup=await main_keyboard(user_id)
    )
    await callback.answer()


@router.callback_query(F.data == 'send_notifications')
async def send_notification_to_subscribers(callback: types.CallbackQuery):
    subscribers = await sync_to_async(list)(
        CustomUser.objects.filter(notifications=True)
    )

    message_text = (
        "Программа мероприятия была обновлена!\n"
        "Используйте кнопку '📅 Программа мероприятия' "
        "для просмотра актуального расписания."
    )

    for user in subscribers:
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text=f"🔔 Уведомление:\n\n{message_text}"
        )

    report_message = "✅ Уведомление успешно отправлено."

    await callback.message.answer(report_message)
    await callback.answer()


@router.callback_query(F.data == 'apply_for_speaker')
async def start_speaker_application(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Пожалуйста, заполните заявку на роль спикера.\n\n"
        "Введите тему вашего выступления:"
    )
    await state.set_state(SpeakerApplicationStates.waiting_for_topic)
    await callback.answer()


@router.message(SpeakerApplicationStates.waiting_for_topic)
async def process_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer("Теперь введите описание вашего выступления:")
    await state.set_state(SpeakerApplicationStates.waiting_for_description)


@router.message(SpeakerApplicationStates.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Расскажите о вашем опыте в этой теме:")
    await state.set_state(SpeakerApplicationStates.waiting_for_experience)


@router.message(SpeakerApplicationStates.waiting_for_experience)
async def process_experience(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=message.from_user.id)

    application = await sync_to_async(SpeakerApplication.objects.create)(
        user=user,
        topic=user_data['topic'],
        description=user_data['description'],
        experience=message.text
    )

    await message.answer(
        "✅ Ваша заявка на роль спикера успешно подана!\n\n"
        f"Тема: {user_data['topic']}\n"
        f"Описание: {user_data['description']}\n"
        f"Опыт: {message.text}\n\n"
        "Организаторы рассмотрят вашу заявку и свяжутся с вами."
    )

    organizers = await sync_to_async(list)(CustomUser.objects.filter(role='organizer'))
    for organizer in organizers:
        await message.bot.send_message(
            chat_id=os.getenv('organizer_chat_id'),
            text=f"Новая заявка спикера!\n\n"
                    f"От: {user.full_name or user.username}\n"
                    f"Тема: {user_data['topic']}\n\n"
                    f"Для просмотра всех заявок перейдите в админку Django"
        )

    await state.clear()