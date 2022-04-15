# SendingMeterReadings
Бот на aiogram для автоматической передачи показаний приборов учета. В данный момент реализована передача показаний на сайт gas-nn.ru

Состоит из двух микросервисов:
- Bot (сам телеграм бот)
- MeterSender (отправщик показаний на сайты ресурсоснабжающих организаций)

В каждом сервисе выполняется логирование в подкаталог `Logs`

Для работы создать в каталоге `Bot` файл '.env' с содержимым:
```
ADMIN=телеграм_ID_админа
BOT_TOKEN=телеграм_токен_бота
PASSWORD_ENCRYPT_KEY=Ключ_для_шифрования_паролей_в_базе_данных_45_символов
db_host=localhost_или_IP
db_port=5432_или_другой
db_user=postgres
db_password=password
db_name=smr
```

в каталоге `MeterSender` файл '.env' с содержимым:
```
PASSWORD_ENCRYPT_KEY=Ключ_для_шифрования_паролей_в_базе_данных_45_символов
gasnn_test_login=логин_для_теста_передачи_gas-nn
gasnn_test_password=пароль_для_теста_передачи_gas-nn
gasnn_test_account_id=лицевой_счет_для_теста_передачи_gas-nn
test_mode=True/False - для отладки
```

Установка необходимых пакетов:
```pycon
pip install -r requirements.txt
```
в каждом микросервисе свой файл requirements.txt
