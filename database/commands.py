import sqlite3
import os
from . import add_test_data, create_db
import config
from cryptography.fernet import Fernet

# db_name = 'db/' + DB_name
db_name = config.DB_name


async def user_is_registered(user_id: int):
    user_info = await get_user_info(user_id)
    return user_info is not None


async def get_user_info(user_id: int):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * from users where id = ?""", [user_id])
    user_info = cursor.fetchone()
    if user_info is None:
        return None
    else:
        return dict(user_info)


async def add_user_info(user_info: dict):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user_data = (user_info.get('id', 0),
                 user_info.get('username', ''),
                 user_info.get('first_name', ''),
                 user_info.get('phone'),
                 user_info.get('email')
                 )
    cursor.execute("""INSERT INTO users VALUES (?, ?, ?, ?, ?)""", user_data)
    conn.commit()


async def reset_database():
    if os.path.isfile(db_name):
        os.remove(db_name)
    create_db.create_tables()
    add_test_data.add_test_data()


async def gasnn_add_account(account_info: dict):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
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
                    account_info.get('auto_sending', False),
                    account_info.get('default_increment', 0)
                    )
    cursor.execute("""INSERT INTO gas_nn_accounts(
    user, name, login, password, account_number, family_name, auto_sending, default_increment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", account_data)
    conn.commit()


async def gasnn_get_account(account_id: int) -> dict:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gas_nn_accounts WHERE id = ?", [account_id])
    row = cursor.fetchone()

    account = dict_factory(cursor, row)

    cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
    encrypted_password = bytes(account.get('password', ''), 'utf-8')
    decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
    account['password'] = decrypted_password

    return account


async def gasnn_get_accounts(user_id):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gas_nn_accounts WHERE User = ?", [user_id])
    accounts = list()
    for row in cursor.fetchall():
        accounts.append(dict_factory(cursor, row))
    return accounts


async def gasnn_get_meter_readings(account_id, number: int = 0) -> list:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    limit = 'LIMIT ' + str(number) if number != 0 else ''
    shell = f"""SELECT * FROM
                (SELECT * FROM gas_nn_meter_readings WHERE account = ?
                ORDER BY date DESC {limit})
                ORDER BY date ASC"""
    cursor.execute(shell, [account_id])
    accounts = list()
    for row in cursor.fetchall():
        dict_row = dict_factory(cursor, row)
        dict_row['is_sent'] = bool(dict_row['is_sent'])
        accounts.append(dict_row)
    return accounts


async def gasnn_get_meter_readings_for_sending(date_from: float, number: int = 0) -> list:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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
        dict_row = dict_factory(cursor, row)
        cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
        encrypted_password = bytes(dict_row.get('password', ''), 'utf-8')
        decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
        dict_row['password'] = decrypted_password
        meter_readings.append(dict_row)
    cursor.execute('DROP VIEW LastMR')
    conn.close()
    return meter_readings


async def gasnn_get_accounts_for_autosending(date_from: float, number: int = 0) -> list:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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
        dict_row = dict_factory(cursor, row)
        cipher = Fernet(config.PASSWORD_ENCRYPT_KEY[-1])
        encrypted_password = bytes(dict_row.get('password', ''), 'utf-8')
        decrypted_password = cipher.decrypt(encrypted_password).decode('utf-8')
        dict_row['password'] = decrypted_password
        meter_readings.append(dict_row)
    return meter_readings


async def gasnn_add_meter_reading(account: int,
                                  date: float,
                                  current_value: float = 0,
                                  is_sent: bool = False,
                                  date_of_sending: int = 0) -> list:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    values = (account, date, current_value, int(is_sent), date_of_sending)
    cursor.execute("""INSERT INTO gas_nn_meter_readings(account, date, current_value, is_sent, date_of_sending)
                      VALUES (?, ?, ?, ?, ?)""", values)
    conn.commit()


async def gasnn_set_attribute_account(account_id: int, attribute: str, value):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE gas_nn_accounts set {} = ? where id = ?".format(attribute), (value, account_id))
    conn.commit()


async def gasnn_delete_account(account_id: int):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gas_nn_meter_readings WHERE account = ?", [account_id])
    cursor.execute("DELETE FROM gas_nn_accounts WHERE id = ?", [account_id])
    conn.commit()


def dict_factory(cursor, row) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
