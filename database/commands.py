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


async def get_gasnn_accounts(user_id):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gas_nn_accounts WHERE User = ?", [user_id])
    accounts = list()
    for row in cursor.fetchall():
        accounts.append(dict_factory(cursor, row))
    return accounts


async def add_gasnn_account(account_info: dict):
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


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d