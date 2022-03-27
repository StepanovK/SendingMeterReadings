from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
from aiogram.utils.callback_data import CallbackData
import database.commands as db
import datetime

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
    meter_readings = await db.get_gasnn_meter_readings(account_id, 5)
    if len(meter_readings.count) == 0:
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
                                         reply_markup=menu
    )

    data = {'account_id': account_id,
            'main_menu_message_id': callback_q.message.message_id,
            'action': callback_data.get('action'),
            'last_action': callback_data.get('last_action'),
            'operator': callback_data.get('operator'),
            'messages_id': []
            }
    data['messages_id'].append(new_message.message_id)

    await state.update_data(data)

    await RegStates.Gas_SM_show.set()

    await bot.answer_callback_query(callback_q.id)


def datestamp_to_str(date, f='%Y.%m.%d'):
    date_time = datetime.datetime.fromtimestamp(date).date()
    return date_time.strftime(format)


# @dp.callback_query_handler(gasnn_account_cbd.filter(), state=RegStates.Gas_SM_show)
# async def change_auto_sending(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
#     await db.set_attribute_gasnn_account(account_id=callback_data.get('id'),
#                                          attribute='auto_sending',
#                                          value=bool(int(callback_data.get('auto_sending'))))
#     answer = await bot.send_message(text='Готово!', chat_id=callback_q.message.chat.id)
#     await delete_message_with_timeout(answer, 2)
#     await delete_message_with_timeout(callback_q.message, 0)
#     await MainStates.MainMenuNavigation.set()
#     await bot.answer_callback_query(callback_q.id)
#
#
# @dp.callback_query_handler(gasnn_change_increment_button.filter(), state=RegStates.Gas_attribute_choose)
# async def change_increment(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
#
#     await db.set_attribute_gasnn_account(account_id=callback_data.get('id'),
#                                          attribute='auto_sending',
#                                          value=bool(callback_data.get('auto_sending')))
#
#     default_increment = callback_data.get('default_increment', 0)
#     message = await bot.send_message(
#         chat_id=callback_q.message.chat.id,
#         text='Введите новое значение (текущее значение: {}):'.format(default_increment))
#
#     data = await state.get_data()
#     data['message_for_delete'] = message
#     await state.update_data(data)
#
#     await callback_q.message.delete()
#
#     await RegStates.Gas_default_increment_input.set()
#
#     await bot.answer_callback_query(callback_q.id)
#
#
# @dp.message_handler(state=RegStates.Gas_default_increment_input)
# async def save_increment_input(message: Message, state: FSMContext):
#
#     new_value = message.text
#
#     try:
#         new_value = int(new_value)
#     except ValueError:
#         answer = await message.answer(text='Введено некорректное значение!')
#         await delete_message_with_timeout(answer, 2)
#
#     data = await state.get_data()
#     account_id = int(data.get('account_id', 0))
#
#     if isinstance(new_value, int) \
#             and isinstance(account_id, int) \
#             and account_id != 0:
#
#         await db.set_attribute_gasnn_account(account_id=account_id, attribute='default_increment', value=new_value)
#
#         answer = await message.answer(text='Новое значение установлено!')
#         await delete_message_with_timeout(answer, 2)
#
#     await message.delete()
#
#     message_for_delete = data.get('message_for_delete')
#     if message_for_delete is not None and isinstance(message_for_delete, Message):
#         await message_for_delete.delete()
#         data['message_for_delete'] = None
#
#     await MainStates.MainMenuNavigation.set()
#
#
# @dp.callback_query_handler(gasnn_delete_account.filter(), state=RegStates.Gas_attribute_choose)
# async def ask_before_delete_account(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
#
#     account_id = int(callback_data.get('id', 0))
#     markup = await yes_no_keyboard(question_id='delete_gasnn_account', callback_data=str(account_id))
#     account_info = await db.get_gasnn_account(account_id)
#     text = 'Вы уверены, что хотите удалить ВСЮ информацию о лицевом счете "{}" ({})?'.format(account_info.get('name'),
#                                                                                              account_info.get('login'))
#     await bot.send_message(chat_id=callback_q.message.chat.id, text=text, reply_markup=markup)
#
#     await RegStates.Gas_delete_account_confirmation.set()
#
#     await callback_q.message.delete()
#
#     await bot.answer_callback_query(callback_q.id)
#
#
# @dp.callback_query_handler(yes_no_cbd.filter(question_id='delete_gasnn_account'),
#                            state=RegStates.Gas_delete_account_confirmation)
# async def delete_account_confirm(callback: CallbackQuery, callback_data: dict, state: FSMContext):
#
#     deletion_confirmed = bool(int(callback_data.get('value', 0)))
#     account_id = int(callback_data.get('callback_data', 0))
#
#     data = await state.get_data()
#
#     if deletion_confirmed:
#         await db.delete_gasnn_account(account_id)
#         message = await bot.send_message(chat_id=callback.message.chat.id,
#                                          text='Аккаунт удалён!')
#         await delete_message_with_timeout(message, 2)
#
#         main_menu_message_id = int(data.get('main_menu_message_id', 0))
#         if main_menu_message_id != 0:
#             markup = await select_operator_menu(operator=data.get('operator'),
#                                                 action=data.get('last_action'),
#                                                 user_id=callback.message.from_user.id,
#                                                 main_menu_message_id=main_menu_message_id)
#             await bot.edit_message_reply_markup(message_id=main_menu_message_id,
#                                                 reply_markup=markup,
#                                                 chat_id=callback.message.chat.id)
#
#     await callback.message.delete()
#     await MainStates.MainMenuNavigation.set()
#     await bot.answer_callback_query(callback.id)
#
#
# @dp.callback_query_handler(gasnn_cancel.filter(), state=RegStates.Gas_attribute_choose)
# async def ask_before_delete_account(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
#     await state.get_data()
#     await MainStates.MainMenuNavigation.set()
#     await callback_q.message.delete()
#     await bot.answer_callback_query(callback_q.id)
#
#
# @dp.message_handler(state=RegStates.Gas_attribute_choose)
# @dp.message_handler(state=RegStates.Gas_delete_account_confirmation)
# async def delete_wrong_message(message: Message, state: FSMContext):
#     if message is not None\
#             and isinstance(message, Message)\
#             and not message.from_user.is_bot:
#         await bot.delete_message(chat_id=state.chat, message_id=message.message_id)


