import fake_useragent
import aiohttp
import asyncio
import json
import config

url = 'https://www.gas-nn.ru'
url_login = 'https://www.gas-nn.ru/auth/login?authType=login'
url_ls_info = 'https://www.gas-nn.ru/api/lk/getLschetInfo'
url_counter_info = 'https://www.gas-nn.ru/api/lk/getCounterInfo'
url_indication = 'https://www.gas-nn.ru/lk/indication'


async def send_mr(account_info: dict):
    async with aiohttp.ClientSession() as session:
        user = fake_useragent.UserAgent().random
        headers = {
            'User-Agent': user,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,fr;q=0.5',
            'Connection': 'keep-alive'
        }
        login_data = {'Login': account_info.get('login', ''),
                      'Password': account_info.get('password', '')}
        params = {
            'authType': 'login',
        }
        responce_authorization = await session.post(url=url_login,
                                                    json=login_data,
                                                    headers=headers,
                                                    params=params)
        print(responce_authorization)

        if responce_authorization.status == 200:
            responce_dict = json.loads(await responce_authorization.text())
            access_token = responce_dict.get('access_token', '')

            headers['access_token'] = access_token
            headers['Authorization'] = 'Bearer ' + access_token
            headers['Referer'] = 'https://www.gas-nn.ru/lk/indication'

            params = {'ls': account_info.get('account_id')}

            ls_info = await session.get(url=url_ls_info, headers=headers, params=params)
            ls_info.encoding = 'utf-8'
            print(ls_info)
            if ls_info.status == 200:
                ls_info_js = json.loads(await ls_info.text())
                print(json.dumps(ls_info_js, indent=4, sort_keys=True, ensure_ascii=False))

            counter_info = await session.get(url=url_counter_info, params=params, headers=headers)
            counter_info.encoding = 'utf-8'
            print(counter_info)
            if counter_info.status == 200:
                counters_info_js = json.loads(await counter_info.text())
                print(json.dumps(counters_info_js, indent=4, sort_keys=True, ensure_ascii=False))
                if len(counters_info_js) > 0:
                    pass


async def send_mrs():
    account_info = {'login': config.gasnn_test_login,
                    'password': config.gasnn_test_password,
                    'account_id': config.gasnn_test_account_id}

    await send_mr(account_info)


def main():
    asyncio.run(send_mrs())


if __name__ == '__main__':
    main()
