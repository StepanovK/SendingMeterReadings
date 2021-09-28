from aiogram import executor
from loader import dp
import handlers.registration
import handlers.navigation


async def on_startup(bot):
    print('\nБот запущен!')


async def on_shutdown(bot):
    print('Бот остановлен!')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
