import sqlite3
from config import DB_name


def create_tables():
    conn = sqlite3.connect(DB_name)
    cursor = conn.cursor()
    with open("database/database_description.sql", "r") as f:
        sql = f.read()
        cursor.executescript(sql)
        conn.commit()


if __name__ == '__main__':
    create_tables()

