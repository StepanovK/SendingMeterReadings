import datetime
import database.commands as db


async def send_gasnn_meter_readings():

    sanding_day_from = 25
    sanding_day_to = 26
    max_number_of_mr_for_sending = 100
    number_of_last_days_for_sending = 20

    time_now = datetime.datetime.now()
    if sanding_day_from <= time_now.day <= sanding_day_to:

        date_from = time_now - datetime.timedelta(days=number_of_last_days_for_sending)
        meter_readings_for_sending = await db.gasnn_get_meter_readings_for_sending(int(date_from.timestamp()),
                                                                                   max_number_of_mr_for_sending)
        print('Показания gas-nn.ru типа переданы')

    else:
        pass

