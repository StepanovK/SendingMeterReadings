from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
import database.commands as db

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State

from .navigation import operator_cbd, yes_no_cbd, yes_no_keyboard, clear_message, \
    select_operator_menu, delete_message_with_timeout, MainStates


class RegStates(StatesGroup):
    Gas_InputName = State()
    Gas_InputLogin = State()
    Gas_InputPassword = State()
    Gas_InputAccountNumber = State()
    Gas_InputFamilyName = State()
    Gas_InputAutoSending = State()
    Gas_InputDefaultIncrement = State()
    Gas_EndInput = State()
    Gas_Confirm = State()


@dp.callback_query_handler(operator_cbd.filter(action='create', operator='gas-nn_ru'),
                           state=MainStates.MainMenuNavigation)
async def start_create(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    message = await bot.send_message(text='Введите описание (Например: "Счетчик на кухне"):',
                                     chat_id=callback.message.chat.id,
                                     disable_notification=True)
    data = {'name': '',
            'login': '',
            'password': '',
            'account_number': '',
            'family_name': '',
            'auto_sending': False,
            'default_increment': 0,
            'messages_id': [],
            'main_menu_message_id': int(callback_data.get('main_menu_message_id', 0)),
            'action': callback_data.get('action'),
            'last_action': callback_data.get('last_action'),
            'operator': callback_data.get('operator')
            }
    data['messages_id'].append(message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputName.set()
    await bot.answer_callback_query(callback.id)


@dp.message_handler(state=RegStates.Gas_InputName)
async def input_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['name'] = message.text
    data['messages_id'].append(message.message_id)
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Введите адрес электронной почты для входа:')
    data['messages_id'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputLogin.set()


@dp.message_handler(state=RegStates.Gas_InputLogin)
async def input_login(message: Message, state: FSMContext):
    data = await state.get_data()
    data['messages_id'].append(message.message_id)
    data['login'] = message.text
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Введите пароль:')
    data['messages_id'].append(new_message.message_id)
    await RegStates.Gas_InputPassword.set()
    await state.update_data(data)


@dp.message_handler(state=RegStates.Gas_InputPassword)
async def input_password(message: Message, state: FSMContext):
    data = await state.get_data()
    data['messages_id'].append(message.message_id)
    data['password'] = message.text
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Введите номер лицевого счета:')
    data['messages_id'].append(new_message.message_id)
    await RegStates.Gas_InputAccountNumber.set()
    await state.update_data(data)


@dp.message_handler(state=RegStates.Gas_InputAccountNumber)
async def input_account_number(message: Message, state: FSMContext):
    data = await state.get_data()
    data['messages_id'].append(message.message_id)
    login = message.text
    try:
        int(login)
    except ValueError:
        login = ''
        text = 'Вы ввели некорректное значение! Номер лицевого счета должен состоять из цифр. Повторите ввод:'
        new_message = await message.answer(text=text)
        data['messages_id'].append(new_message.message_id)
    if login != '':
        data['account_number'] = login
        await clear_message(state.chat, data['messages_id'])
        new_message = await message.answer(text='Введите фамилию владельца')
        data['messages_id'].append(new_message.message_id)
        await RegStates.Gas_InputFamilyName.set()
    await state.update_data(data)


@dp.message_handler(state=RegStates.Gas_InputFamilyName)
async def input_family_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['family_name'] = message.text
    yes_no_kb = await yes_no_keyboard()
    data['messages_id'].append(message.message_id)
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Включить автопередачу показаний?', reply_markup=yes_no_kb)
    data['messages_id'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputAutoSending.set()


@dp.callback_query_handler(yes_no_cbd.filter(), state=RegStates.Gas_InputAutoSending)
async def input_auto_sending(call: CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    data['auto_sending'] = bool(int(callback_data.get('value', 0)))
    await RegStates.Gas_InputDefaultIncrement.set()
    await clear_message(state.chat, data['messages_id'])
    if data.get('auto_sending', False):
        new_message = await call.message.answer(text='Введите среднемесячное значение для автоматической передачи')
        data['messages_id'].append(new_message.message_id)
        await state.update_data(data)
    else:
        await state.update_data(data)
        await RegStates.Gas_EndInput.set()
        await end_input(state=state)
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=RegStates.Gas_InputDefaultIncrement)
async def input_default_increment(message: Message, state: FSMContext):
    data = await state.get_data()
    data['messages_id'].append(message.message_id)
    default_increment = message.text
    try:
        default_increment = float(default_increment)
    except ValueError:
        default_increment = ''
        text = 'Вы ввели некорректное значение! ' \
               'Значение для автопередачи показаний должно состоять из цифр. Повторите ввод:'
        new_message = await message.answer(text=text)
        data['messages_id'].append(new_message.message_id)
        await state.update_data(data)
    if isinstance(default_increment, float):
        data['default_increment'] = default_increment
        await clear_message(state.chat, data['messages_id'])
        await state.update_data(data)
        await RegStates.Gas_EndInput.set()
        await end_input(state=state)


async def end_input(state: FSMContext):
    data = await state.get_data()

    message_text = "Вы ввели следующие данные:" \
                   "\nназвание: {name}" \
                   "\nл.с.: {account_number}" \
                   "\nфамилия: {family_name}" \
                   "\nлогин: {login}" \
                   "\nавтопередача показаний {auto_sending}"""

    message_text = message_text.format(
        name=data['name'],
        account_number=data['account_number'],
        family_name=data['family_name'],
        login=data['login'],
        auto_sending='ВКЛЮЧЕНА' if data['auto_sending'] else 'ВЫКЛЮЧЕНА')

    if data['auto_sending']:
        message_text += '\nзначение для автоматической передачи: {}'.format(data['default_increment'])

    new_message = await bot.send_message(chat_id=state.chat,
                                         text=message_text,
                                         reply_markup=confirm_keyboard())
    data['messages_id'].append(new_message.message_id)

    await state.update_data(data)
    await RegStates.Gas_Confirm.set()


def confirm_keyboard():
    markup = Markup()
    confirm_button = Button(text='Подтвердить', callback_data='gas_confirm')
    markup.add(confirm_button)
    cancel_button = Button(text='Отмена', callback_data='gas_clear')
    markup.add(cancel_button)
    return markup


@dp.callback_query_handler(text='gas_clear', state=RegStates.Gas_Confirm)
async def clear_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await clear_message(state.chat, data.get('messages_id', []))
    await MainStates.MainMenuNavigation.set()
    await bot.answer_callback_query(callback.id)


@dp.callback_query_handler(text='gas_confirm', state=RegStates.Gas_Confirm)
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['user'] = callback.message.chat.id
    await db.gasnn_add_account(data)
    await MainStates.MainMenuNavigation.set()
    await bot.answer_callback_query(callback.id)
    await clear_message(state.chat, data.get('messages_id', []))
    main_menu_message_id = int(data.get('main_menu_message_id', 0))
    if main_menu_message_id != 0:
        markup = await select_operator_menu(operator=data.get('operator'),
                                            action=data.get('last_action'),
                                            user_id=callback.message.chat.id,
                                            main_menu_message_id=main_menu_message_id)
        await bot.edit_message_reply_markup(message_id=main_menu_message_id,
                                            reply_markup=markup,
                                            chat_id=callback.message.chat.id)


@dp.message_handler(state=RegStates.Gas_InputAutoSending)
@dp.message_handler(state=RegStates.Gas_Confirm)
async def delete_wrong_message(message: Message, state: FSMContext):
    if message is not None \
            and isinstance(message, Message) \
            and not message.from_user.is_bot:
        await bot.delete_message(chat_id=state.chat, message_id=message.message_id)
