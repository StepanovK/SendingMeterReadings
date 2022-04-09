import datetime
import database.commands as db
from . import gasnn_ru_sander


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

    print('Показания gas-nn.ru типа переданы')


async def send_reported_mr(number_of_last_days_for_sending, max_number_of_mr_for_sending, test_mode):
    time_now = datetime.datetime.now()
    date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)

    meter_readings_for_sending = await db.gasnn_get_meter_readings_for_sending(
        float(date_from.timestamp()),
        max_number_of_mr_for_sending)

    for mr in meter_readings_for_sending:

        if test_mode:
            print('Передача показаний: {}'.format(mr))

        readings = {mr.get('account_number'): mr.get('current_value')}
        auth_settings = {
            'login': mr.get('login'),
            'password': mr.get('password'),
            'account_number': mr.get('account_number'),
        }

        await gasnn_ru_sander.send_readings(auth_settings, readings, test_mode=test_mode)

        if test_mode:
            print('Передано показание {} от {} по лицевому счету {}'.format(
                mr.get('current_value'),
                datetime.datetime.fromtimestamp(mr.get('date')),
                mr.get('account_number')
            )
            )


async def send_autoincremented_mr(number_of_last_days_for_sending, max_number_of_mr_for_sending, test_mode):
    time_now = datetime.datetime.now()
    date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)

    meter_readings_for_sending = await db.gasnn_get_accounts_for_autosending(
        float(date_from.timestamp()),
        max_number_of_mr_for_sending)

    for mr in meter_readings_for_sending:

        if test_mode:
            print('Передача показаний: {}'.format(mr))

        # readings = {mr.get('account_number'): mr.get('current_value')}
        # auth_settings = {
        #     'login': mr.get('login'),
        #     'password': mr.get('password'),
        #     'account_number': mr.get('account_number'),
        # }
        #
        # await gasnn_ru_sander.send_readings(auth_settings, readings, test_mode=test_mode)
        #
        # if test_mode:
        #     print('Передано показание {} от {} по лицевому счету {}'.format(
        #         mr.get('current_value'),
        #         datetime.datetime.fromtimestamp(mr.get('date')),
        #         mr.get('account_number')
        #     )
        #     )
