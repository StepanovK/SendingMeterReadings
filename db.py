import sqlite3
from config import DB_name


async def user_is_registered(user_id: int):
    user_info = await get_user_info(user_id)
    return user_info is not None


async def get_user_info(user_id: int):
    conn = sqlite3.connect(DB_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * from users where id = ?""", [user_id])
    user_info = cursor.fetchone()
    if user_info is None:
        return None
    else:
        return dict(user_info)


async def add_user_info(user_info: dict):
    conn = sqlite3.connect(DB_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user_data = (user_info.get('id', 0),
                 user_info.get('username', ''),
                 user_info.get('first_name', ''),
                 user_info.get('phone'),
                 user_info.get('mail')
                 )
    cursor.execute("""INSERT INTO users VALUES (?, ?, ?, ?, ?)""", [user_data])

