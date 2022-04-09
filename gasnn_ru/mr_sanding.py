import datetime
import database.commands as db
from . import gasnn_ru_sander


async def send_gasnn_meter_readings(test_mode=False):

    sanding_day_from = 25
    sanding_day_to = 26
    max_number_of_mr_for_sending = 100
    number_of_last_days_for_sending = 20


    time_now = datetime.datetime.now()
    if sanding_day_from <= time_now.day <= sanding_day_to or test_mode:

        date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)

        meter_readings_for_sending = await db.gasnn_get_meter_readings_for_sending(int(date_from.timestamp()),
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

        print('Показания gas-nn.ru типа переданы')

    else:
        pass

