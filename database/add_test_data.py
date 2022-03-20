import sqlite3
import config


def add_test_data():
    conn = sqlite3.connect(config.DB_name)
    cursor = conn.cursor()
    with open("database/test_data.sql", "r") as f:
        sql = f.read()
        cursor.executescript(sql)
        conn.commit()


if __name__ == '__main__':
    add_test_data()

