from aiogram import executor
from loader import dp, bot
from config import ADMINS
import mr_sanding
import asyncio
import multiprocessing
import threading
import schedule
import handlers.registration
import handlers.navigation
import handlers.gasnn_edition
import handlers.gasnn_registration
import handlers.gasnn_meters_readings_sending


def start_polling():
    # loop = asyncio.new_event_loop()
    executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown) #, loop=loop)


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


def start_sending():
    loop = asyncio.new_event_loop()
    # loop = asyncio.get_event_loop()
    task = loop.create_task(send_all_meter_readings())
    loop.run_until_complete(task)
    # loop.run_until_complete(send_all_meter_readings())
    # asyncio.set_event_loop(loop)


async def send_all_meter_readings():
    while True:
        await asyncio.sleep(20)
        try:
            await mr_sanding.send_all_meter_readings()
        except Exception as ex:
            print(f'Во время отправки показаний возникла ошибка:\n{ex}')


# def start_process(func: callable):
#     func()

# proc = multiprocessing.Process(target=start_sending)
# proc.start()
# proc2 = multiprocessing.Process(target=start_polling)
# proc2.start()

# while True:
#     pass


if __name__ == '__main__':

    pool = multiprocessing.Pool()
    pool.apply_async(start_sending)
    pool.apply_async(start_polling)
    pool.close()
    pool.join()
    # multiprocessing.freeze_support()
    # while True:
    #     pass
#
#     # tasks = [start_sending]
#     start_polling()
#     proc = multiprocessing.Process(target=start_sending)
#     proc.start()
#     proc.join()
    # proc2 = multiprocessing.Process(target=start_polling)
    # proc2.start()
    # proc2.join()
    # proc.join()
    # procs = [multiprocessing.Process(target=start_sending) for f in tasks]

    # for proc in procs:
    #     proc.start()

    # for proc in procs:
    #     proc.join()

    # sending_thread = threading.Thread(target=start_sending, name='sending_thread')
    # sending_thread.start()
    #
    # # bot_thread = threading.Thread(target=start_polling, name='bot_thread')
    # # bot_thread.start()
    #
    # start_polling()





