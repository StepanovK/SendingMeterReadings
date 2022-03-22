from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
import database.commands as db

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State

from .navigation import operator_cbd, yes_no_cbd, yes_no_keyboard


class RegStates(StatesGroup):
    Gas_InputName = State()
    Gas_InputLogin = State()
    Gas_InputFamilyName = State()
    Gas_InputAutoSending = State()
    Gas_InputDefaultIncrement = State()
    Gas_Confirm = State()


@dp.callback_query_handler(operator_cbd.filter(action='create', operator='gas-nn_ru'), state=None)
async def start_create(callback: CallbackQuery, state: FSMContext):
    await state.reset_state()
    message = await bot.send_message(text='Введите описание (Например: "Счетчик на кухне")',
                                     chat_id=callback.from_user.id,
                                     disable_notification=True)
    data = {'name': '',
            'login': '',
            'family_name': '',
            'auto_sending': False,
            'default_increment': 0,
            'messages_id': []}
    data['messages_id'].append(message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputName.set()


@dp.message_handler(state=RegStates.Gas_InputName)
async def input_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data['name'] = message.text
    data['messages_id'].append(message.message_id)
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Введите номер лицевого счета')
    data['messages_id'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputLogin.set()


@dp.message_handler(state=RegStates.Gas_InputLogin)
async def input_login(message: Message, state: FSMContext):
    data = await state.get_data()
    data['login'] = message.text
    data['messages_id'].append(message.message_id)
    await clear_message(state.chat, data['messages_id'])
    new_message = await message.answer(text='Введите фамилию владельца')
    data['messages_id'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.Gas_InputFamilyName.set()


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
async def input_login(call: CallbackQuery, callback_data: dict, state: FSMContext):
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
        await end_input(message=None, state=state)


@dp.message_handler(state=RegStates.Gas_InputDefaultIncrement)
async def end_input(message: Message, state: FSMContext):
    data = await state.get_data()
    if message is not None:
        data['messages_id'].append(message.message_id)
        if data.get('auto_sending', True):
            data['default_increment'] = int(message.text)
            await state.update_data(data)
    await clear_message(state.chat, data['messages_id'])
    message_text = 'Вы ввели следующие данные: ' \
                   '\nИмя: {}' \
                   '\nл.с.: {}' \
                   '\nфамилия: {}' \
                   '\nавтопередача показаний {}'.format(data['name'],
                                                        data['login'],
                                                        data['family_name'],
                                                        'ВКЛЮЧЕНА' if data['auto_sending'] else 'ВЫКЛЮЧЕНА')
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
    await state.reset_state()


@dp.callback_query_handler(text='gas_confirm', state=RegStates.Gas_Confirm)
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['user'] = callback.message.from_user.id
    await db.add_gasnn_account(data)
    await state.reset_state()
    await clear_message(state.chat, data.get('messages_id', []))


@dp.message_handler(state=RegStates.Gas_InputAutoSending)
@dp.message_handler(state=RegStates.Gas_Confirm)
async def delete_wrong_message(message: Message, state: FSMContext):
    if message is not None \
            and not message.from_user.is_bot:
        await bot.delete_message(chat_id=state.chat, message_id=message.message_id)


async def clear_message(chat_id, messages_id):
    for message_id in messages_id:
        await bot.delete_message(chat_id, message_id)
    messages_id.clear()

