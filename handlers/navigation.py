from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
# from aiogram.utils import callback_data
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
import database.commands as db
from loader import dp
import config


operators_cbd = CallbackData('show_operators_menu', 'action')
operator_cbd = CallbackData('show_operator', 'operator', 'action')
main_menu_cbd = CallbackData('main_menu', 'last_action')
gasnn_account_cbd = CallbackData('gasnn_account', 'id', 'action')
yes_no_cbd = CallbackData('yes-no', 'value')


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
    button1 = Button(text='Редактировать приборы учета', callback_data=operators_cbd.new(action='edit'))
    main_markup.add(button1)
    button2 = Button(text='Передать показания', callback_data=operators_cbd.new(action='send_mr'))
    main_markup.add(button2)
    return main_markup


def first_menu():
    markup = Markup()
    button1 = Button(text='Зарегистрироваться', callback_data='start_registration')
    markup.insert(button1)
    return markup


@dp.callback_query_handler(operators_cbd.filter())
async def select_operator(call: CallbackQuery, callback_data: dict):
    await show_operators_menu(call, callback_data.get('action', ''))


async def show_operators_menu(call: CallbackQuery, action):
    menu = operator_menu(action)
    await call.message.edit_text(text='Выберите оператора', reply_markup=menu)


def operator_menu(action):
    markup = Markup()
    callback_data = operator_cbd.new(operator='gas-nn_ru', action=action)
    button1 = Button(text='НижегородЭнергоГазРасчет (gas-nn.ru)', callback_data=callback_data)
    markup.add(button1)
    main_menu_button = Button(text='<< В главное меню', callback_data=main_menu_cbd.new(last_action=action))
    markup.add(main_menu_button)
    return markup


@dp.callback_query_handler(operator_cbd.filter(action='edit'))
# @dp.callback_query_handler(operator_cbd.filter(action='create'))
async def select_operator(call: CallbackQuery, callback_data: dict):
    action = callback_data.get('action')
    operator = callback_data.get('operator')
    if operator == 'gas-nn_ru':
        menu = await meter_edit_menu_gasnn_ru(call.message.from_user.id, action)
    else:
        raise ValueError('Для поставщика услуг "{}" не создана клавиатура!'.format(operator))
    if action == 'edit':
        add_button_callback_data = operator_cbd.new(operator=operator, action='create')
        add_button = Button(text='(+) Добавить аккаунт', callback_data=add_button_callback_data)
        menu.add(add_button)
    go_back_button = Button(text='<< Назад', callback_data=operators_cbd.new(action=action))
    menu.add(go_back_button)
    await call.message.edit_text(text='Выберите аккаунт для редактирования', reply_markup=menu)


async def meter_edit_menu_gasnn_ru(user_id, action):
    accounts = await db.get_gasnn_accounts(user_id)
    menu = Markup()
    for account in accounts:
        # print(account)
        text = '{} ({})'.format(account.get('name'), account.get('login'))
        callback_data = gasnn_account_cbd.new(id=account.get('id'), action=action)
        account_button = Button(text=text, callback_data=callback_data)
        menu.add(account_button)
    return menu


async def yes_no_keyboard():
    yn_keyboard = Markup()
    yes = Button(text='Да', callback_data=yes_no_cbd.new(value=1))
    yn_keyboard.add(yes)
    no = Button(text='Нет', callback_data=yes_no_cbd.new(value=0))
    yn_keyboard.add(no)
    return yn_keyboard


# @dp.message_handler(state=None)
# async def end_input(message: Message, state: FSMContext):
#     pass
