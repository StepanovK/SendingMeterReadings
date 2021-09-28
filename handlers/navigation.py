from aiogram.types import CallbackQuery, Message, User
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
import db.db as db
from loader import dp


@dp.message_handler(commands=['start'])
async def show_start_menu(message: Message):
    if await db.user_is_registered(message.from_user.id):
        await message.answer(reply_markup=main_menu(), text='Выберите, что нужно сделать')
    else:
        text = """Добро пожаловать!
                  \nЭтот бот поможет вам передавать показания приборов учета даже когда вы забываете это сделать.
                  \nДля начала нужно зарегистрироваться и добавить приборы учета. Начнём?"""
        await message.answer(reply_markup=first_menu(), text=text)


def main_menu():
    main_markup = Markup()
    button1 = Button(text='Редактировать приборы учета', callback_data='open_operators_menu/edit')
    main_markup.add(button1)
    button2 = Button(text='Передать показания', callback_data='open_operators_menu/send_mr')
    main_markup.add(button2)
    return main_markup


def first_menu():
    markup = Markup()
    button1 = Button(text='Зарегистрироваться', callback_data='start_registration')
    markup.insert(button1)
    return markup


# @dp.callback_query_handler()
# async def do_something(callback_data: CallbackQuery, **kwargs):
#     pass

