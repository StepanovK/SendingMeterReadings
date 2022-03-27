from aiogram import executor
from loader import dp, bot
from config import ADMINS
import handlers.registration
import handlers.registration_gasnn
import handlers.edition_gasnn
import handlers.navigation


async def on_startup(dp: dp):
    text_message = 'Бот запущен!'
    print('\n' + text_message)
    # await send_to_admins(text_message)


async def on_shutdown(dp: dp):
    text_message = 'Бот остановлен'
    print('\n' + text_message)
    # await send_to_admins(text_message)


async def send_to_admins(text_message: str):
    for admin_id in ADMINS:
        await bot.send_message(text=text_message, chat_id=admin_id)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
