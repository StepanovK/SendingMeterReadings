from environs import Env
import loguru

logger = loguru.logger
logger.add('Logs/bot_log.log', format='{time} {level} {message}', rotation='512 KB', compression='zip')

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMIN")
PASSWORD_ENCRYPT_KEY = env.str("PASSWORD_ENCRYPT_KEY")

db_host = env.str("db_host")
db_port = env.int("db_port")
db_user = env.str("db_user")
db_password = env.str("db_password")
db_name = env.str("db_name")
