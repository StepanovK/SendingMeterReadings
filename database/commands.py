import sqlite3
import os
from . import add_test_data, create_db
import config


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
    account_data = (account_info.get('user', ''),
                    account_info.get('name', ''),
                    account_info.get('login', ''),
                    account_info.get('family_name', ''),
                    account_info.get('auto_sending', False),
                    account_info.get('default_increment', 0)
                    )
    cursor.execute("""INSERT INTO gas_nn_accounts(user, name, login, family_name, auto_sending, default_increment)
                        VALUES (?, ?, ?, ?, ?, ?)""", account_data)
    conn.commit()


async def gasnn_get_account(account_id: int) -> dict:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gas_nn_accounts WHERE id = ?", [account_id])
    row = cursor.fetchone()
    return dict_factory(cursor, row)


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


async def gasnn_add_meter_reading(account: int,
                                  date: int,
                                  current_value: int = 0,
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
