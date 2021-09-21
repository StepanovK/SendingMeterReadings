import sqlite3
import config


def create_tables():
    conn = sqlite3.connect(config.DB_name)
    cursor = conn.cursor()

    cursor.execute("""
                    PRAGMA foreign_keys = on
                    """)

    cursor.execute("""
                   CREATE TABLE users
                   (id integer primary key NOT NULL,
                   username varchar NOT NULL,
                   first_name varchar,
                   phone varchar,
                   mail varchar)
                   """)

    cursor.execute("""
                   CREATE TABLE gas_nn_accounts
                   (id integer primary key,
                   user integer NOT NULL,
                   name varchar NOT NULL,
                   login varchar NOT NULL,
                   family_name varchar NOT NULL,
                   auto_sending bit NOT NULL DEFAULT 0,
                   default_increment float NOT NULL DEFAULT 0,
                   FOREIGN KEY (user) REFERENCES users(id))
                   """)

    cursor.execute("""
                   CREATE TABLE gas_nn_meter_readings
                   (account integer  NOT NULL,
                   date integer NOT NULL DEFAULT 0,
                   current_value float NOT NULL DEFAULT 0,
                   is_sent bit NOT NULL DEFAULT 0,
                   date_of_sending integer NOT NULL DEFAULT 0,
                   FOREIGN KEY (account) REFERENCES gas_nn_accounts(id))
                   """)

    conn.commit()


if __name__ == '__main__':
    create_tables()

