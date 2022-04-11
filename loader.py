from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import loguru


logger = loguru.logger
logger.add('bot_log.log', format='{time} {level} {message}', rotation='512 KB', compression='zip')

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
