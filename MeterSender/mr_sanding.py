import asyncio
from gasnn_ru.mr_sanding import send_gasnn_meter_readings
from config import logger, debug


async def send_all_meter_readings():
    while True:
        try:
            await send_gasnn_meter_readings(test_mode=not debug)
        except Exception as ex:
            logger.error(f'Во время отправки показаний возникла ошибка:\n{ex}')
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(send_all_meter_readings())
