from loader import logger
import config
from cryptography.fernet import Fernet
import psycopg2
import psycopg2.extras


def get_pg_connection():
    try:
        connection = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password
        )
        return connection
    except Exception as ex:
        logger.error("Проблема при подключении к базе данных PostgreSQL", ex)
        return None


def get_bd_connection():
    try:
        connection = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password,
            database=config.db_name
        )
        return connection
    except Exception as ex:
        logger.error("Проблема при подключении к базе данных PostgreSQL", ex)
        return None


async def user_is_registered(user_id: int):
    user_info = await get_user_info(user_id)
    return user_info is not None


async def get_user_info(user_id: int):
    conn = get_bd_connection()
    # conn.row_factory = sqlite3.Row
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("""SELECT * from users where id = %s""", [user_id])
        user_info = cursor.fetchone()
        if user_info is not None:
            return dict(user_info)


async def add_user_info(user_info: dict):
    conn = get_bd_connection()
    # conn.row_factory = sqlite3.Row
    with conn.cursor() as cursor:
        user_data = (user_info.get('id', 0),
                     user_info.get('username', ''),
                     user_info.get('first_name', ''),
                     user_info.get('phone'),
                     user_info.get('email')
                     )
        cursor.execute("""INSERT INTO users VALUES (%s, %s, %s, %s, %s)""", user_data)
        conn.commit()


def reset_database():
    conn = get_pg_connection()
    conn.autocommit = True
    logger.info('Обновление базы данных:')
    with conn.cursor() as cursor:
        logger.info('1 - Удаление БД. Начало')
        cursor.execute(
            f"""DROP DATABASE IF EXISTS {config.db_name};"""
        )
        logger.info('1 - Удаление БД. Конец')

        logger.info('2 - Создание БД. Начало')
        try:
            cursor.execute(
                f"""CREATE DATABASE {config.db_name}
                    WITH 
                    OWNER = postgres
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'Russian_Russia.1251'
                    LC_CTYPE = 'Russian_Russia.1251'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1;"""
            )
            logger.info('2 - Создание БД. Конец')
        except Exception as ex:
            logger.error(f'Не удалось создать базу данных.\n{ex}')
    conn.close()

    with open("DB_actions/database_description.sql", "r") as f:
        sql = f.read()
        conn = get_bd_connection()
        with conn.cursor() as cursor:
            logger.info('3 - Создание таблиц в новой БД. Начало')
            cursor.execute(sql)
            conn.commit()
            logger.info('3 - Создание таблиц в новой БД. Конец')
        conn.close()
    logger.info('База данных создана!')


async def add_test_data():
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        with open("DB_actions/test_data.sql", "r") as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()
    conn.close()


async def gasnn_add_account(account_info: dict):
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        cursor = conn.cursor()

        cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
        encrypted_password = cipher.encrypt(bytes(account_info.get('password', ''), 'utf-8'))
        encrypted_password = encrypted_password.decode('utf-8')

        account_data = (account_info.get('user', ''),
                        account_info.get('name', ''),
                        account_info.get('login', ''),
                        encrypted_password,
                        account_info.get('account_number', ''),
                        account_info.get('family_name', ''),
                        int(account_info.get('auto_sending', False)),
                        account_info.get('default_increment', 0)
                        )
        cursor.execute("""INSERT INTO gas_nn_accounts(
        \"user\", name, login, password, account_number, family_name, auto_sending, default_increment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", account_data)
        conn.commit()
    conn.close()


async def gasnn_get_account(account_id: int) -> dict:
    conn = get_bd_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM gas_nn_accounts WHERE id = %s", [account_id])
        row = cursor.fetchone()

        account = dict(row)

        conn.close()

        cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
        encrypted_password = bytes(account.get('password', ''), 'utf-8')
        decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
        account['password'] = decrypted_password

        return account


async def gasnn_get_accounts(user_id):
    conn = get_bd_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM gas_nn_accounts WHERE \"user\" = %s", [user_id])
        accounts = list()
        for row in cursor.fetchall():
            accounts.append(dict(row))
        conn.close()
        return accounts


async def gasnn_get_meter_readings(account_id, number: int = 0) -> list:
    conn = get_bd_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        limit = 'LIMIT ' + str(number) if number != 0 else ''
        shell = f"""SELECT * FROM
                    (SELECT * FROM gas_nn_meter_readings WHERE account = %s
                    ORDER BY \"date\" DESC {limit}) AS gas_nn_mr
                    ORDER BY \"date\" ASC"""
        cursor.execute(shell, [account_id])
        accounts = list()
        for row in cursor.fetchall():
            dict_row = dict(row)
            dict_row['is_sent'] = bool(dict_row['is_sent'])
            accounts.append(dict_row)
        conn.close()
        return accounts


async def gasnn_get_meter_readings_for_sending(date_from: float, number: int = 0) -> list:
    conn = get_bd_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:

        limit = 'LIMIT ' + str(number) if number != 0 else ''
        date_filter = f'WHERE gas_nn_meter_readings.date >= {date_from}' if date_from > 0 else ''

        shell = f"""CREATE VIEW LastMR AS
                SELECT
                gas_nn_meter_readings.account,
                max(gas_nn_meter_readings.date) AS date
                FROM  gas_nn_meter_readings
                {date_filter}
                GROUP BY account
                ORDER BY date
                {limit}"""
        cursor.execute(shell)

        shell = """SELECT
                gas_nn_accounts.account_number,
                gas_nn_accounts.user,
                gas_nn_accounts.login,
                gas_nn_accounts.password,
                gas_nn_meter_readings.id,
                gas_nn_meter_readings.account AS account_id,
                gas_nn_meter_readings.current_value,
                gas_nn_meter_readings.date
                FROM gas_nn_meter_readings
    
                INNER JOIN LastMR
                ON
                    gas_nn_meter_readings.account = LastMR.account
                    AND gas_nn_meter_readings.date = LastMR.date
    
                INNER JOIN gas_nn_accounts
                ON
                    gas_nn_meter_readings.account = gas_nn_accounts.id
    
                WHERE gas_nn_meter_readings.is_sent = 0"""
        cursor.execute(shell)

        meter_readings = list()
        for row in cursor.fetchall():
            dict_row = dict(row)
            cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
            encrypted_password = bytes(dict_row.get('password', ''), 'utf-8')
            decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
            dict_row['password'] = decrypted_password
            meter_readings.append(dict_row)
        cursor.execute('DROP VIEW LastMR')
        conn.close()
        return meter_readings


async def gasnn_get_accounts_for_autosending(date_from: float, number: int = 0) -> list:
    conn = get_bd_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:

        limit = 'LIMIT ' + str(number) if number != 0 else ''

        shell = f"""SELECT
                gas_nn_accounts.id AS account_id,
                gas_nn_accounts.name,
                gas_nn_accounts.login,
                gas_nn_accounts.password,
                gas_nn_accounts.account_number,
                gas_nn_accounts.family_name,
                gas_nn_accounts.default_increment
                FROM gas_nn_accounts
                LEFT JOIN gas_nn_meter_readings
                ON
                gas_nn_accounts.id = gas_nn_meter_readings.account
                AND gas_nn_meter_readings.date >= {date_from}
                WHERE
                 gas_nn_accounts.auto_sending = 1
                AND gas_nn_meter_readings.id is NULL
                {limit}"""
        cursor.execute(shell)

        meter_readings = list()
        for row in cursor.fetchall():
            dict_row = dict(row)
            cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
            encrypted_password = bytes(dict_row.get('password', ''), 'utf-8')
            decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
            dict_row['password'] = decrypted_password
            meter_readings.append(dict_row)
        conn.close()
        return meter_readings


async def gasnn_add_meter_reading(account: int,
                                  date: float,
                                  current_value: float = 0,
                                  is_sent: bool = False,
                                  date_of_sending: int = 0):
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        values = (account, date, current_value, int(is_sent), date_of_sending)
        cursor.execute("""INSERT INTO gas_nn_meter_readings(account, date, current_value, is_sent, date_of_sending)
                          VALUES (%s, %s, %s, %s, %s)""", values)
        conn.commit()
    conn.close()


async def gasnn_set_attribute_account(account_id: int, attribute: str, value):
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE gas_nn_accounts set {} = %s where id = %s".format(attribute), (value, account_id))
        conn.commit()


async def gasnn_update_meter_reading(mr_id: int, new_info: dict):
    if len(new_info) == 0:
        return
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        attribute_texts = []
        values = []
        for attribute in new_info:
            attribute_texts.append('{} = %s'.format(attribute))
            values.append(new_info[attribute])
        shell = """UPDATE gas_nn_meter_readings
        SET
        {} 
        WHERE id = %s""".format(',\n'.join(attribute_texts))
        values.append(mr_id)
        cursor.execute(shell, values)
        conn.commit()
    conn.close()


async def gasnn_delete_account(account_id: int):
    conn = get_bd_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM gas_nn_meter_readings WHERE account = %s", [account_id])
        cursor.execute("DELETE FROM gas_nn_accounts WHERE id = %s", [account_id])
        conn.commit()
    conn.close()
