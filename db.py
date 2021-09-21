import sqlite3
from config import DB_name


def user_is_registered(user_id: int):
    user_info = get_user_info(user_id)
    return user_info is not None


def get_user_info(user_id: int):
    conn = sqlite3.connect(DB_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""SELECT * from users where id = ?""", [user_id])
    user_info = cursor.fetchone()
    if user_info is None:
        return None
    else:
        return dict(user_info)

