import os
import asyncio
from textwrap import dedent
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from dotenv import load_dotenv
from handlers import router


async def set_menu_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить подробную информацию о боте")
    ])


async def main():
    load_dotenv()

    bot = Bot(token=os.environ['TG_BOT_TOKEN'])

    if not bot.token:
        print(dedent("""\
            Ошибка: Не указан TG_BOT_TOKEN.
            Убедитесь, что он задан в переменных окружения.
        """))
        return

    dp = Dispatcher()
    dp.include_router(router)

    await set_menu_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())