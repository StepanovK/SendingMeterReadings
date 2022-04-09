# SendingMeterReadings
Бот на aiogram для автоматической передачи показаний приборов учета

Для работы создать в каталоге файл '.env' с содержимым:
```
ADMIN=телеграм_ID_админа
BOT_TOKEN=телеграм_токен_бота
PASSWORD_ENCRYPT_KEY=Ключ_для_шифрования_паролей_в_базе_данных_45_символов
gasnn_test_login=логин_для_теста_передачи_gas-nn
gasnn_test_password=пароль_для_теста_передачи_gas-nn
gasnn_test_account_id=лицевой_счет_для_теста_передачи_gas-nn
```

Установка необходимых пакетов:
```pycon
pip install -r requirements.txt
```