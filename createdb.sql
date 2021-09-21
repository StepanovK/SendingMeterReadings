create table users(
    id int primary key,
    telegram_id varchar(255)
);

create table accaunts(
    id int primary key,
    FOREIGN KEY(user_id) REFERENCES users(id)
);