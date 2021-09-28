import sqlite3
import config


def create_tables():
    conn = sqlite3.connect(config.DB_name)
    cursor = conn.cursor()
    with open("database_description.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


if __name__ == '__main__':
    create_tables()

