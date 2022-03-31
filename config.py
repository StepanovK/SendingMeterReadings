from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMIN")
PASSWORD_ENCRYPT_KEY = env.list("PASSWORD_ENCRYPT_KEY")
DB_name = 'smr.db'



