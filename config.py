from environs import Env
import loguru

logger = loguru.logger
logger.add('Logs/log.txt', format='{time} {level} {message}', rotation='512 KB', compression='zip')

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMIN")
PASSWORD_ENCRYPT_KEY = env.str("PASSWORD_ENCRYPT_KEY")

db_host = 'localhost'
db_port = 5432
db_user = env.str("POSTGRES_USER")
db_password = env.str("POSTGRES_PASSWORD")
db_name = env.str("db_name")

debug = True
