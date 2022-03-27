INSERT INTO users (id, username, first_name) 
    VALUES (300925449, 'duffman152', 'duffman152');

INSERT INTO gas_nn_accounts (user, name, login, family_name, auto_sending) 
    VALUES (300925449, 'Счетчик в квартире', '051000322434', 'Кривенков', 0);

INSERT INTO gas_nn_accounts (user, name, login, family_name, auto_sending)
    VALUES (300925449, 'Счетчик в доме', '051000507028', 'Степанов', 1);

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1627076470, 617, 1, 1627249270);

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1629326470, 617, 1, 1629927670);

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1632519670, 617, 0, 0);

