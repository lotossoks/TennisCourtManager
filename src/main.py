import asyncio
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.exceptions import TelegramForbiddenError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.types import ChatMember

load_dotenv('../.env.example')
TOKEN = getenv('TOKEN')

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def get_chat_roles(chat_id: int):
    admins: list[ChatMember] = await bot.get_chat_administrators(chat_id)

    roles = {}
    for admin in admins:
        user = admin.user
        roles[user.id] = {
            "username": user.username,
            "full_name": user.full_name,
            "status": admin.status,
            "custom_title": admin.custom_title,
        }
    return roles


@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f'Привет! Чтобы добавить меня в чат, необходимо:\n'
        f'1. Перейти в ваш чат\n'
        f'2. Нажать на кнопку "добавить участников"\n'
        f'  a) Найти Booking bot\n'
        f'  b) Добавить Booking bot в чат\n'
        f'3. Нажать на бота и назначить администратором\n'
    )


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        chat_id = message.chat.id
        roles = await get_chat_roles(chat_id)
        for user_id, data in roles.items():
            print(f"ID: {user_id}, Имя: {data['full_name']}, Роль: {data['status']}")

    except TelegramForbiddenError:
        pass


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
