from environs import Env
import loguru

logger = loguru.logger
logger.add('sending_log.log', format='{time} {level} {message}', rotation='512 KB', compression='zip')

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMIN")
PASSWORD_ENCRYPT_KEY = env.list("PASSWORD_ENCRYPT_KEY")

gasnn_test_login = env.str("gasnn_test_login")
gasnn_test_password = env.str("gasnn_test_password")
gasnn_test_account_id = env.str("gasnn_test_account_id")

DB_name = 'smr.db'
