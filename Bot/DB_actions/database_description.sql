CREATE TABLE users
                   (id integer primary key NOT NULL,
                   username varchar NOT NULL,
                   first_name varchar,
                   phone varchar,
                   email varchar);

CREATE TABLE gas_nn_accounts
                   (id serial primary key,
                   "user" integer NOT NULL,
                   name varchar NOT NULL,
                   login varchar NOT NULL,
                   password varchar(300) NOT NULL,
                   account_number varchar NOT NULL,
                   family_name varchar NOT NULL,
                   auto_sending integer NOT NULL DEFAULT 0,
                   default_increment float NOT NULL DEFAULT 0,
                   FOREIGN KEY ("user") REFERENCES users(id) ON DELETE CASCADE);

CREATE TABLE gas_nn_meter_readings
                   (id serial primary key,
                   account integer NOT NULL,
                   "date" float NOT NULL DEFAULT 0,
                   current_value float NOT NULL DEFAULT 0,
                   is_sent integer NOT NULL DEFAULT 0,
                   date_of_sending float NOT NULL DEFAULT 0,
                   FOREIGN KEY (account) REFERENCES gas_nn_accounts(id) ON DELETE CASCADE);
