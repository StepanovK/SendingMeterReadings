from aiogram import executor
from loader import dp, bot
from config import ADMINS
import mr_sanding
import schedule
import asyncio
import handlers.registration
import handlers.navigation
import handlers.gasnn_edition
import handlers.gasnn_registration
import handlers.gasnn_meters_readings_sending


async def on_startup(dp: dp):
    text_message = 'Бот запущен!'
    print('\n' + text_message)
    asyncio.create_task(send_all_meter_readings())
    # await send_to_admins(text_message)


async def on_shutdown(dp: dp):
    text_message = 'Бот остановлен'
    print('\n' + text_message)
    # await send_to_admins(text_message)


async def send_to_admins(text_message: str):
    for admin_id in ADMINS:
        await bot.send_message(text=text_message, chat_id=admin_id)


async def send_all_meter_readings():
    while True:
        try:
            await mr_sanding.send_all_meter_readings()
        except Exception as ex:
            print(f'Во время отправки показаний возникла ошибка:\n{ex}')
        await asyncio.sleep(60)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)





