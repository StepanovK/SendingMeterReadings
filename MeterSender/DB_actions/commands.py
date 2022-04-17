import config
from config import logger
from cryptography.fernet import Fernet
import psycopg2
import psycopg2.extras


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
        connection_info = f'host={config.db_host}, port={config.db_port},' \
                          f' user={config.db_user} password={config.db_password}'
        logger.error(f"Проблема при подключении к базе данных {config.db_name}\n({connection_info}):", ex)
        return None


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

