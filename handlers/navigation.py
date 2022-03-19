from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
# from aiogram.utils import callback_data
from aiogram.utils.callback_data import CallbackData
import database.commands as db
from loader import dp
import config


operators_cbd = CallbackData('show_operators_menu', 'next_action')
operator_cbd = CallbackData('show_operator', 'operator', 'next_action')
main_menu_cbd = CallbackData('main_menu', 'last_action')


@dp.message_handler(commands=['stop'])
async def stop_bot(message: Message):
    if str(message.from_user.id) in config.ADMINS:
        pass
        # dp.stop_polling()
    else:
        await message.answer(text='У вас нет прав на выполнение этой команды!')


@dp.message_handler(commands=['start'])
async def show_start_menu(message: Message):
    if await db.user_is_registered(message.from_user.id):
        await message.answer(reply_markup=main_menu(), text='Выберите, что нужно сделать')
    else:
        text = """Добро пожаловать!
                  \nЭтот бот поможет вам передавать показания приборов учета даже когда вы забываете это сделать.
                  \nДля начала нужно зарегистрироваться и добавить приборы учета. Начнём?"""
        await message.answer(reply_markup=first_menu(), text=text)


@dp.callback_query_handler(main_menu_cbd.filter())
async def show_main_menu(call: CallbackQuery, callback_data):
    await call.message.edit_text(text='Выберите, что нужно сделать', reply_markup=main_menu())


@dp.message_handler(commands=['reset'])
async def reset_database(message: Message):
    if str(message.from_user.id) in config.ADMINS:
        await db.reset_database()
        await message.reply('База данных очищена! Нажмите команду /start')


def main_menu():
    main_markup = Markup()
    button1 = Button(text='Редактировать приборы учета', callback_data=operators_cbd.new(next_action='edit'))
    main_markup.add(button1)
    button2 = Button(text='Передать показания', callback_data=operators_cbd.new(next_action='send_mr'))
    main_markup.add(button2)
    return main_markup


def first_menu():
    markup = Markup()
    button1 = Button(text='Зарегистрироваться', callback_data='start_registration')
    markup.insert(button1)
    return markup


@dp.callback_query_handler(operators_cbd.filter())
async def select_operator(call: CallbackQuery, callback_data: dict):
    await show_operators_menu(call, callback_data.get('next_action', ''))


async def show_operators_menu(call: CallbackQuery, next_action):
    # chat_id = call.message.chat.id
    # await dp.bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
    menu = operator_menu(next_action)
    # await dp.bot.send_message(text='Выберите оператора', reply_markup=menu, chat_id=chat_id)
    await call.message.edit_text(text='Выберите оператора', reply_markup=menu)


def operator_menu(next_action):
    markup = Markup()
    callback_data = operator_cbd.new(operator='gas-nn_ru', next_action=next_action)
    button1 = Button(text='НижегородЭнергоГазРасчет (gas-nn.ru)', callback_data=callback_data)
    markup.add(button1)
    main_menu_button = Button(text='<< В главное меню', callback_data=main_menu_cbd.new(last_action=next_action))
    markup.add(main_menu_button)
    return markup


@dp.callback_query_handler()
async def select_operator(call: CallbackQuery, callback_data: dict):
    pass


