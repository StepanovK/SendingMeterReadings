from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
from aiogram.utils.callback_data import CallbackData
from datetime import datetime
import database.commands as db

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State

from .navigation import gasnn_account_cbd,\
    yes_no_cbd, yes_no_keyboard, select_operator_menu, delete_message_with_timeout, MainStates


gasnn_input_readings = CallbackData('gasnn_input_readings', 'id')
gasnn_cancel_input_readings = CallbackData('gasnn_cancel_input', 'id')


class RegStates(StatesGroup):
    Gas_SM_show = State()
    Gas_InputReadings = State()


@dp.callback_query_handler(gasnn_account_cbd.filter(action='send_mr'), state=MainStates.MainMenuNavigation)
async def start_edit(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):

    account_id = callback_data.get('id')
    meter_readings = await db.gasnn_get_meter_readings(account_id, 5)
    if len(meter_readings) == 0:
        text_message = 'Показания отсутствуют'
    else:
        text_message = 'Предыдущие показания:'
        for mr in meter_readings:
            if mr.get('is_sent', False):
                date_of_sending = mr.get('date_of_sending')
                sent_text = 'передано {}'.format(datestamp_to_str(date_of_sending))
            else:
                sent_text = 'не передано'
            mr_text = '{}: {} ({})'.format(datestamp_to_str(mr.get('date')),
                                           mr.get('current_value'),
                                           sent_text)
            text_message += '\n' + mr_text

    menu = Markup()
    input_button = Button(text='Ввести показания', callback_data=gasnn_input_readings.new(id=account_id))
    menu.add(input_button)
    input_button = Button(text='Отмена', callback_data=gasnn_cancel_input_readings.new(id=account_id))
    menu.add(input_button)

    new_message = await bot.send_message(chat_id=callback_q.message.chat.id,
                                         text=text_message,
                                         reply_markup=menu)
    state_data = {'account_id': account_id,
                  'main_menu_message_id': callback_q.message.message_id,
                  'action': callback_data.get('action'),
                  'last_action': callback_data.get('last_action'),
                  'last_mr': None,
                  'operator': callback_data.get('operator'),
                  'messages_id': []
                  }
    state_data['messages_id'].append(new_message.message_id)

    if len(meter_readings) >= 1:
        state_data['last_mr'] = meter_readings[-1]

    await state.update_data(state_data)

    await RegStates.Gas_SM_show.set()

    await bot.answer_callback_query(callback_q.id)


def datestamp_to_str(date, f='%Y.%m.%d'):
    date_time = datetime.fromtimestamp(date).date()
    return date_time.strftime(f)


@dp.callback_query_handler(gasnn_cancel_input_readings.filter(), state=RegStates.Gas_SM_show)
async def change_auto_sending(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.answer_callback_query(callback_q.id)
    await callback_q.message.delete()
    await MainStates.MainMenuNavigation.set()


@dp.callback_query_handler(gasnn_input_readings.filter(), state=RegStates.Gas_SM_show)
async def change_increment(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):

    await bot.answer_callback_query(callback_q.id)

    message_text = 'Введите новое значение для передачи:'

    state_data = await state.get_data()

    last_mr = state_data.get('last_mr')
    if last_mr is not None:
        if last_mr.get('is_sent', False):
            sending_text = 'было передано {}'.format(datestamp_to_str(last_mr.get('date_of_sending')))
        else:
            sending_text = 'не было передано'
        value = last_mr.get('current_value', 0)
        date = datestamp_to_str(last_mr.get('date'))
        notes_text = f'Последнее значение {value} было отправлено боту {date} и {sending_text}'
        message_text = notes_text + '\n' + message_text

    await callback_q.message.delete_reply_markup()
    await callback_q.message.edit_text(text=message_text)

    state_data['message_for_delete'] = callback_q.message
    await state.update_data(state_data)

    await RegStates.Gas_InputReadings.set()


@dp.message_handler(state=RegStates.Gas_InputReadings)
async def save_increment_input(message: Message, state: FSMContext):

    new_value = message.text

    try:
        new_value = float(new_value)
    except ValueError:
        answer = await message.answer(text='Введено некорректное значение!')
        await delete_message_with_timeout(answer, 2)

    state_data = await state.get_data()
    account_id = int(state_data.get('account_id', 0))

    if isinstance(new_value, float) \
            and isinstance(account_id, int) \
            and account_id != 0:

        await db.gasnn_add_meter_reading(account=account_id,
                                         date=datetime.now().timestamp(),
                                         current_value=new_value)
        message_text = f'Значение {new_value} принято ботом. Оно будет передано в положенное время передачи'
        answer = await message.answer(text=message_text)
        await delete_message_with_timeout(answer, 4)

        message_for_delete = state_data.get('message_for_delete')
        if message_for_delete is not None and isinstance(message_for_delete, Message):
            await message_for_delete.delete()
            state_data['message_for_delete'] = None

        await state.reset_state(with_data=True)
        await MainStates.MainMenuNavigation.set()

    await message.delete()


@dp.message_handler(state=RegStates.Gas_SM_show)
async def delete_wrong_message(message: Message, state: FSMContext):
    if message is not None\
            and isinstance(message, Message)\
            and not message.from_user.is_bot:
        await bot.delete_message(chat_id=state.chat, message_id=message.message_id)

