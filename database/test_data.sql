INSERT INTO users (id, username, first_name) 
    VALUES (300925449, 'duffman152', 'duffman152');

INSERT INTO gas_nn_accounts (user, name, login, password, account_number, family_name, auto_sending)
    VALUES (
      300925449,
     'Счетчик в квартире',
     'doom2good@mail.ru',
     'gAAAAABiRh_nOOkZbCZEVSAbOXWXeDpYtx5VLcgasovTSe7UPqlKhF3zg8SQKuW8vsg7_Uc-OW7rFveNyIdIl7zeiOOEqNG5srwokxzbReGGAOa5AEKyWY4=',
     '051000322434',
     'Степанов',
     0
     );

INSERT INTO gas_nn_accounts (user, name, login, password, account_number, family_name, auto_sending)
    VALUES (
      300925449,
     'Счетчик в доме',
     'doom2good@mail.ru',
     'gAAAAABiRh3y3u33Xb3waSXv2TMLoJg-m8lTFw898aF4DL17rEXN5fRJhIxTOKH_WgrEVsZez6vlhN_urQfpDP1PB59DuFOk9A==',
     '051000507028',
     'Степанов',
      1
      );

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1627076470, 617, 1, 1627249270);

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1629326470, 617, 1, 1629927670);

INSERT INTO gas_nn_meter_readings (account, date, current_value, is_sent, date_of_sending)
    VALUES (2, 1632519670, 617, 0, 1629928670);

