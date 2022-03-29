from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
# from aiogram.utils import callback_data
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import database.commands as db
from loader import dp, bot
from typing import Union
import config
import time

operators_cbd = CallbackData('show_operators_menu', 'action')
operator_cbd = CallbackData('show_operator', 'operator', 'action', 'last_action', 'main_menu_message_id')
main_menu_cbd = CallbackData('main_menu', 'last_action')
gasnn_account_cbd = CallbackData('gasnn_account', 'id', 'action', 'last_action', 'operator', 'main_menu_message_id')
yes_no_cbd = CallbackData('yes-no', 'value', 'question_id', 'callback_data')


class MainStates(StatesGroup):
    MainMenuNavigation = State()


@dp.message_handler(commands=['stop'], state='*')
async def stop_bot(message: Message, state: FSMContext):
    if str(message.chat.id) in config.ADMINS:
        pass
        # dp.stop_polling()
    else:
        await message.answer(text='У вас нет прав на выполнение этой команды!')


@dp.message_handler(commands=['start'], state='*')
async def show_start_menu(message: Message, state: FSMContext):
    text, reply_markup = await text_and_markup_for_main_menu(message.chat.id)
    await message.answer(text=text, reply_markup=reply_markup)
    await MainStates.MainMenuNavigation.set()
    await message.delete()


async def text_and_markup_for_main_menu(user_id: int):
    if await db.user_is_registered(user_id):
        text = 'Выберите, что нужно сделать'
        reply_markup = main_menu()
    else:
        text = """Добро пожаловать!
                  \nЭтот бот поможет вам передавать показания приборов учета даже когда вы забываете это сделать.
                  \nСначала нужно зарегистрироваться и добавить приборы учета. Начнём?"""
        reply_markup = first_menu()
    return text, reply_markup


@dp.callback_query_handler(main_menu_cbd.filter(), state=MainStates.MainMenuNavigation)
async def show_main_menu(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_text(text='Выберите, что нужно сделать', reply_markup=main_menu())
    await bot.answer_callback_query(call.id)
    await MainStates.MainMenuNavigation.set()


@dp.message_handler(commands=['reset'], state='*')
async def reset_database(message: Message, state: FSMContext):
    if str(message.chat.id) in config.ADMINS:
        await db.reset_database()
        await message.reply('База данных очищена! Нажмите команду /start')
    await state.reset_state()


def main_menu():
    main_markup = Markup(one_time_keyboard=True)
    button1 = Button(text='Редактировать приборы учета', callback_data=operators_cbd.new(action='menu_edit'))
    main_markup.add(button1)
    button2 = Button(text='Передать показания', callback_data=operators_cbd.new(action='menu_snd_mr'))
    main_markup.add(button2)
    return main_markup


def first_menu():
    markup = Markup(one_time_keyboard=True)
    button1 = Button(text='Зарегистрироваться', callback_data='start_registration')
    markup.insert(button1)
    return markup


@dp.callback_query_handler(operators_cbd.filter(), state=MainStates.MainMenuNavigation)
async def select_operator(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await show_operators_menu(call, callback_data.get('action', ''))
    await bot.answer_callback_query(call.id)
    await MainStates.MainMenuNavigation.set()


async def show_operators_menu(call: CallbackQuery, action):
    menu = operator_menu(action)
    await call.message.edit_text(text='Выберите оператора', reply_markup=menu)


def operator_menu(action: str):
    markup = Markup()
    callback_data = operator_cbd.new(operator='gas-nn_ru',
                                     action=action,
                                     last_action=action,
                                     main_menu_message_id='0')
    button1 = Button(text='НижегородЭнергоГазРасчет (gas-nn.ru)', callback_data=callback_data)
    markup.add(button1)
    main_menu_button = Button(text='<< В главное меню', callback_data=main_menu_cbd.new(last_action=action))
    markup.add(main_menu_button)
    return markup


@dp.callback_query_handler(operator_cbd.filter(action='menu_edit'), state=MainStates.MainMenuNavigation)
async def select_operator_for_edit(call_or_message: Union[CallbackQuery, Message], callback_data: dict, state: FSMContext):

    if isinstance(call_or_message, CallbackQuery):
        message = call_or_message.message
        await bot.answer_callback_query(call_or_message.id)
    else:
        message = call_or_message

    menu = await select_operator_menu(operator=callback_data.get('operator'),
                                      action=callback_data.get('action'),
                                      user_id=message.chat.id,
                                      main_menu_message_id=message.message_id)

    await message.edit_text(text='Выберите аккаунт для редактирования', reply_markup=menu)

    await MainStates.MainMenuNavigation.set()


@dp.callback_query_handler(operator_cbd.filter(action='menu_snd_mr'), state=MainStates.MainMenuNavigation)
async def select_operator_sending_mr(call_or_message: Union[CallbackQuery, Message], callback_data: dict, state: FSMContext):

    if isinstance(call_or_message, CallbackQuery):
        message = call_or_message.message
        await bot.answer_callback_query(call_or_message.id)
    else:
        message = call_or_message

    menu = await select_operator_menu(operator=callback_data.get('operator'),
                                      action=callback_data.get('action'),
                                      user_id=message.chat.id,
                                      main_menu_message_id=message.message_id)

    await message.edit_text(text='Выберите аккаунт для передачи показаний', reply_markup=menu)

    await MainStates.MainMenuNavigation.set()


async def select_operator_menu(operator, action, user_id, main_menu_message_id=0):

    if action == 'menu_edit':
        next_action = 'edit'
    elif action == 'menu_snd_mr':
        next_action = 'send_mr'
    else:
        next_action = ''

    if operator == 'gas-nn_ru':
        menu = await meter_menu_gasnn_ru(user_id, next_action, action, main_menu_message_id)
    else:
        raise ValueError('Для поставщика услуг "{}" не создана клавиатура!'.format(operator))
    if action == 'menu_edit':
        add_button_callback_data = operator_cbd.new(operator=operator,
                                                    action='create',
                                                    last_action=action,
                                                    main_menu_message_id=main_menu_message_id)
        add_button = Button(text='(+) Добавить аккаунт', callback_data=add_button_callback_data)
        menu.add(add_button)

    go_back_button = Button(text='<< Назад', callback_data=operators_cbd.new(action=action))
    menu.add(go_back_button)

    return menu


async def meter_menu_gasnn_ru(user_id, action, last_action, main_menu_message_id=0, operator='gas-nn_ru'):
    accounts = await db.gasnn_get_accounts(user_id)
    menu = Markup()
    for account in accounts:
        # print(account)
        text = '{} ({})'.format(account.get('name'), account.get('login'))
        callback_data = gasnn_account_cbd.new(id=account.get('id'),
                                              action=action,
                                              last_action=last_action,
                                              main_menu_message_id=main_menu_message_id,
                                              operator=operator)
        account_button = Button(text=text, callback_data=callback_data)
        menu.add(account_button)
    return menu


async def yes_no_keyboard(question_id: str = '', callback_data: str = ''):

    question_id = 'None' if question_id == '' else question_id
    callback_data = 'None' if callback_data == '' else callback_data

    yn_keyboard = Markup(one_time_keyboard=True)
    yes = Button(text='Да', callback_data=yes_no_cbd.new(value=1,
                                                         question_id=question_id,
                                                         callback_data=callback_data))
    yn_keyboard.add(yes)
    no = Button(text='Нет', callback_data=yes_no_cbd.new(value=0,
                                                         question_id=question_id,
                                                         callback_data=callback_data))
    yn_keyboard.add(no)
    return yn_keyboard


async def delete_message_with_timeout(message: Message, timeout: int = 0):
    time.sleep(timeout)
    await message.delete()


@dp.message_handler(state=MainStates.MainMenuNavigation)
async def delete_wrong_message(message: Message, state: FSMContext):

    if message is not None \
            and isinstance(message, Message)\
            and not message.from_user.is_bot:

        await bot.delete_message(chat_id=state.chat, message_id=message.message_id)


@dp.callback_query_handler(state=None)
async def go_home_menu(call: CallbackQuery = None, callback_data: dict = None, state: FSMContext = None):

    """
    Если состояние неизвестно, значит нужно вернуться в главное меню
    """

    await bot.answer_callback_query(call.id)

    text, reply_markup = await text_and_markup_for_main_menu(call.message.chat.id)
    try:
        await call.message.edit_text(text=text, reply_markup=reply_markup)
    except Exception:
        print('Не удалось вернуть пользователя {} в главное меню. Возможно, он уже в нём.'.format(call.message.chat.id))

    await MainStates.MainMenuNavigation.set()


async def clear_message(chat_id: int, messages_id: list):
    for message_id in messages_id:
        await bot.delete_message(chat_id, message_id)
    messages_id.clear()


