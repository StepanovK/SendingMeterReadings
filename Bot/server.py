from aiogram import executor
from loader import dp, bot, logger
from config import ADMINS
import argparse
import DB_actions.commands as db
import aiogram
import handlers.registration
import handlers.navigation
import handlers.gasnn_edition
import handlers.gasnn_registration
import handlers.gasnn_meters_readings_sending

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--resetdb", default=0, help="This is the 'resetdb' variable")


def start_polling():
    executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown)


async def on_startup(dp: dp):
    text_message = 'Бот запущен!'
    logger.info(text_message)
    # await send_to_admins(text_message)


async def on_shutdown(dp: dp):
    text_message = 'Бот остановлен'
    logger.info(text_message)
    # await send_to_admins(text_message)


async def send_to_admins(text_message: str):
    for admin_id in ADMINS:
        await bot.send_message(text=text_message, chat_id=admin_id)


if __name__ == '__main__':
    args = parser.parse_args()
    if str(args.resetdb) == '1':
        db.reset_database()
    start_polling()
