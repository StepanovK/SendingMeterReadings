import datetime
from DB_actions import commands as db
from . import gasnn_ru_sander
from config import logger


@logger.catch()
async def send_gasnn_meter_readings(test_mode=False):
    """
    Передаёт показания из базы на сайт gas-nn.ru. Настройки отправки:
    - sanding_day_from - дата начала передачи показаний
    - sanding_day_to - дата окончания передачи показаний
    - seconds_for_autosending - секунды до конца дня sanding_day_to для старта передачи автоматических показаний
    - max_number_of_mr_for_sending - макс количество показаний для передачи за раз (размер выборки)
    - number_of_last_days_for_sending - количество дней, за которое берутся переданные показания

    :param test_mode: Для отладки.
    """
    sanding_day_from = 23
    sanding_day_to = 25
    seconds_for_autosending = 60 * 60 * 3
    max_number_of_mr_for_sending = 100
    number_of_last_days_for_sending = 23

    connection = db.get_bd_connection()
    if connection is None:
        logger.error('Не удалось подключиться к базе данных. Отправка показаний gas-nn.ru отменена!')
        return

    time_now = datetime.datetime.now()

    if test_mode:
        sanding_day_from = time_now.day - 1
        sanding_day_to = time_now.day
        seconds_for_autosending = 60 * 60 * 24

    if sanding_day_from <= time_now.day <= sanding_day_to:
        await send_reported_mr(number_of_last_days_for_sending,
                               max_number_of_mr_for_sending,
                               test_mode)

    end_of_sending = datetime.datetime(time_now.year, time_now.month, sanding_day_to, 23, 59, 59)
    time_to_autosending = end_of_sending.timestamp() - seconds_for_autosending

    if sanding_day_from <= time_now.day <= sanding_day_to and time_to_autosending <= time_now.timestamp():
        await send_autoincremented_mr(number_of_last_days_for_sending,
                                      max_number_of_mr_for_sending,
                                      test_mode)

    logger.info('Показания gas-nn.ru переданы')


@logger.catch()
async def send_reported_mr(number_of_last_days_for_sending, max_number_of_mr_for_sending, test_mode=False):
    time_now = datetime.datetime.now()
    date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)

    meter_readings_for_sending = await db.gasnn_get_meter_readings_for_sending(
        float(date_from.timestamp()),
        max_number_of_mr_for_sending)

    for mr in meter_readings_for_sending:

        if test_mode:
            logger.info('Передача показаний: {}'.format(mr))

        readings = []
        reading = {
            'id': mr.get('id'),
            'ls': mr.get('account_number', ''),
            'account_id': mr.get('account_id'),
            'value': mr.get('current_value', 0),
            'date': mr.get('date', 0),
            'auto_sending': False,
            'increment': 0
            ,
        }
        readings.append(reading)
        auth_settings = {
            'login': mr.get('login'),
            'password': mr.get('password'),
            'account_id': mr.get('account_id'),
        }

        readings = await gasnn_ru_sander.send_readings(auth_settings, readings, test_mode=test_mode)

        for reading in readings:
            mr_id = reading.get('id')
            if mr_id is None or id == 0 or id == '':
                continue
            new_info = {
                'is_sent': 1,
                'date_of_sending': reading.get('date_of_sending')
            }
            await db.gasnn_update_meter_reading(mr_id, new_info)

        logger.info('Передано показание {} от {} по лицевому счету {}'.format(
            mr.get('current_value'),
            datetime.datetime.fromtimestamp(mr.get('date')),
            mr.get('account_number')
        )
        )


@logger.catch()
async def send_autoincremented_mr(number_of_last_days_for_sending, max_number_of_mr_for_sending, test_mode=False):
    time_now = datetime.datetime.now()
    date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)

    meter_readings_for_sending = await db.gasnn_get_accounts_for_autosending(
        date_from.timestamp(),
        max_number_of_mr_for_sending)

    for mr in meter_readings_for_sending:

        if test_mode:
            logger.info('Передача показаний: {}'.format(mr))

        readings = []
        reading = {
            'id': None,
            'ls': mr.get('account_number', ''),
            'account_id': mr.get('account_id'),
            'value': 0,
            'date': time_now.timestamp(),
            'auto_sending': True,
            'increment': mr.get('default_increment', 0)
            ,
        }
        readings.append(reading)
        auth_settings = {
            'login': mr.get('login'),
            'password': mr.get('password'),
            'account_id': mr.get('account_id'),
        }

        readings = await gasnn_ru_sander.send_readings(auth_settings, readings, test_mode=test_mode)

        for reading in readings:
            value = reading.get('value')
            if value is None or value == 0:
                continue
            await db.gasnn_add_meter_reading(account=reading.get('account_id'),
                                             date=reading.get('date_of_sending'),
                                             current_value=value,
                                             is_sent=True,
                                             date_of_sending=reading.get('date_of_sending'))

            logger.info('Передано автоматическое показание {}'.format(reading))
