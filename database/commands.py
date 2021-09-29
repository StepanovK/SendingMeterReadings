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
                 user_info.get('mail')
                 )
    cursor.execute("""INSERT INTO users VALUES (?, ?, ?, ?, ?)""", user_data)
    conn.commit()


async def reset_database():
    if os.path.isfile(db_name):
        os.remove(db_name)
    create_db.create_tables()
    add_test_data.add_test_data()


