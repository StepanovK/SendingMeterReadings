from environs import Env
import loguru

logger = loguru.logger
logger.add('Logs/sending_log.log', format='{time} {level} {message}', rotation='512 KB', compression='zip')

env = Env()
env.read_env()

PASSWORD_ENCRYPT_KEY = env.str("PASSWORD_ENCRYPT_KEY")
test_mode = env.bool("test_mode")
gasnn_test_login = env.str("gasnn_test_login")
gasnn_test_password = env.str("gasnn_test_password")
gasnn_test_account_id = env.str("gasnn_test_account_id")

db_host = env.str("db_host")
db_port = env.int("db_port")
db_user = env.str("db_user")
db_password = env.str("db_password")
db_name = env.str("db_name")
