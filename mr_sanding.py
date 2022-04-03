from gasnn_ru import mr_sanding


async def send_all_meter_readings():
    await mr_sanding.send_gasnn_meter_readings()


