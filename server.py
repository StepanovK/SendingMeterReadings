from aiogram import executor, types
from loader import dp
import navigation
import registration


async def on_startup():
    print('\nБот запущен!')


async def on_shutdown():
    print('Бот остановлен!')


if __name__ == '__main__':
    print('\nБот запущен!')
    # navigation.dp = dp
    executor.start_polling(dp)#, on_startup=on_startup, on_shutdown=on_shutdown)
