import fake_useragent
import aiohttp
import asyncio
import json
import config
import datetime

url = 'https://www.gas-nn.ru'
url_login = 'https://www.gas-nn.ru/auth/login?authType=login'
url_ls_info = 'https://www.gas-nn.ru/api/lk/getLschetInfo'
url_counter_info = 'https://www.gas-nn.ru/api/lk/getCounterInfo'
url_counter_history = 'https://www.gas-nn.ru/api/lk/getCounterHistory'
url_indication = 'https://www.gas-nn.ru/lk/indication'


def main():
    asyncio.run(send_mrs())


async def send_mrs():
    account_info = {'login': config.gasnn_test_login,
                    'password': config.gasnn_test_password}
    readings = [{config.gasnn_test_account_id: 123}]

    await send_readings(account_info, readings, True)


async def send_readings(account_info: dict, readings: list, test_mode=False):
    sent_mr = []

    async with aiohttp.ClientSession() as session:

        headers = {}
        session_started = await start_session(session, account_info, headers, test_mode)

        if not session_started:
            print(f'Не удалось авторизоваться на сайте gas-nn.ru под учетной записью {account_info}')
            return sent_mr

        for reading in readings:

            account_number = reading.get('ls', '')

            ls_info = await get_ls_info(session, headers, account_number, test_mode)

            auto_sending = reading.get('auto_sending', False)

            if auto_sending:

                last_mr_sending = await get_last_mr_sending(session, headers, account_number, test_mode)

                if last_mr_sending is None or last_mr_sending.get('value', 0) == 0:
                    print(f'Не удалось получить последнее переданное значение по лицевому счету {account_number}')

                    continue

                last_value = last_mr_sending.get('value', 0)
                value_for_send = last_value + reading.get('increment', 0)

                # TODO: Отправка показаний

                response = {
                    'id': reading.get('id'),
                    'account_id': reading.get('account_id'),
                    'account_number': account_number,
                    'value': value_for_send,
                    'date_of_sending': datetime.datetime.now().timestamp()
                }

                sent_mr.append(response)

            else:

                # TODO: Отправка показаний

                response = {
                    'id': reading.get('id'),
                    'account_id': reading.get('account_id'),
                    'account_number': account_number,
                    'value': 00000000000000000000000000000000000000,
                    'date_of_sending': datetime.datetime.now().timestamp()
                }

                sent_mr.append(response)

    session.close()

    return sent_mr


async def start_session(session, account_info: dict, headers: dict = None, test_mode=False):
    if headers is None:
        headers = {}

    user = fake_useragent.UserAgent().random

    headers['User-Agent'] = user
    headers['Accept'] = 'application/json, text/plain, */*'
    headers['Accept-Language'] = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,fr;q=0.5'
    headers['Connection'] = 'keep-alive'

    login_data = {'Login': account_info.get('login', ''),
                  'Password': account_info.get('password', '')}
    params = {
        'authType': 'login',
    }
    response_authorization = await session.post(url=url_login,
                                                json=login_data,
                                                headers=headers,
                                                params=params)
    print_if_test_mode(response_authorization, test_mode)

    if response_authorization.status == 200:

        response_dict = json.loads(await response_authorization.text())
        access_token = response_dict.get('access_token', '')

        headers['access_token'] = access_token
        headers['Authorization'] = 'Bearer ' + access_token
        headers['Referer'] = url_indication

    else:
        print(f'Ошибка авторизации для аккаунта {account_info} \n {response_authorization}')

    return response_authorization.status == 200


async def get_last_mr_sending(session, headers, account_number, test_mode):
    params = {'ls': str(account_number)}

    counter_history = await session.get(url=url_counter_history, params=params, headers=headers)
    counter_history.encoding = 'utf-8'
    print_if_test_mode(counter_history, test_mode)

    last_sending = None

    if counter_history.status == 200:
        counter_history_js = json.loads(await counter_history.text())

        last_time_of_sending = 0

        for sending in counter_history_js:
            date_time_str = sending.get('date')
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f')
            date_timestamp = date_time_obj.timestamp()
            sending['date_timestamp'] = date_timestamp
            if last_time_of_sending < date_timestamp:
                last_time_of_sending = date_timestamp
                last_sending = sending

        print_if_test_mode(json.dumps(counter_history_js, indent=4, sort_keys=True, ensure_ascii=False),
                           test_mode)

    return last_sending


async def get_ls_info(session, headers, account_number, test_mode):
    params = {'ls': str(account_number)}

    ls_info = await session.get(url=url_ls_info, headers=headers, params=params)
    ls_info.encoding = 'utf-8'
    print_if_test_mode(ls_info, test_mode)
    if ls_info.status == 200:
        ls_info_text = await ls_info.text()
        ls_info = json.loads(ls_info_text)
        print_if_test_mode(json.dumps(ls_info, indent=4, sort_keys=True, ensure_ascii=False), test_mode)
    else:
        print(f'Ошибка при получении данных по лицевому счету {account_number}')
        ls_info = None

    return ls_info


def print_if_test_mode(message, test_mode: bool = False):
    if test_mode:
        print(message)


if __name__ == '__main__':
    main()
