from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
from aiogram.utils.callback_data import CallbackData
import database.commands as db
import time

from loader import dp, bot, logger
from aiogram.dispatcher.filters.state import StatesGroup, State

from .navigation import gasnn_account_cbd,\
    yes_no_cbd, yes_no_keyboard, select_operator_menu, delete_message_with_timeout, MainStates


gasnn_change_auto_sending = CallbackData('gasnn_change_auto_sending', 'id', 'auto_sending')
gasnn_change_increment_button = CallbackData('gasnn_change_increment_button', 'id', 'default_increment')
gasnn_delete_account = CallbackData('gasnn_delete_account', 'id')
gasnn_cancel = CallbackData('gasnn_cancel', 'id')


class RegStates(StatesGroup):
    Gas_attribute_choose = State()
    Gas_default_increment_input = State()
    Gas_delete_account_confirmation = State()


@dp.callback_query_handler(gasnn_account_cbd.filter(action='edit'), state=MainStates.MainMenuNavigation)
async def start_edit(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):

    account_id = callback_data.get('id')
    account_info = await db.gasnn_get_account(account_id)
    auto_sending = account_info.get('auto_sending', False)

    menu = Markup(one_time_keyboard=True)

    if auto_sending:
        text = 'Отключить автопередачу показаний'
    else:
        text = 'Включить автопередачу показаний'
    callback = gasnn_change_auto_sending.new(id=account_id, auto_sending=int(not auto_sending))
    auto_sending_button = Button(text=text, callback_data=callback)
    menu.add(auto_sending_button)

    default_increment = account_info.get('default_increment', 0)
    callback = gasnn_change_increment_button.new(id=account_id, default_increment=default_increment)
    text = 'Изменить значение автопередачи ({})'.format(default_increment)
    default_increment_button = Button(text=text, callback_data=callback)
    menu.add(default_increment_button)

    callback = gasnn_delete_account.new(id=account_id)
    dell_button = Button(text='(-) УДАЛИТЬ АККАУНТ', callback_data=callback)
    menu.add(dell_button)

    callback = gasnn_cancel.new(id=account_id)
    cancel_button = Button(text='Отмена', callback_data=callback)
    menu.add(cancel_button)

    await bot.send_message(
        chat_id=callback_q.message.chat.id,
        text='Выбирите, что хотите сделать с аккаунтом "{}":'.format(account_info.get('name')),
        reply_markup=menu
    )

    data = {'account_id': account_id,
            'main_menu_message_id': callback_q.message.message_id,
            'action': callback_data.get('action'),
            'last_action': callback_data.get('last_action'),
            'operator': callback_data.get('operator')
            }
    await state.update_data(data)

    await RegStates.Gas_attribute_choose.set()

    await bot.answer_callback_query(callback_q.id)


@dp.callback_query_handler(gasnn_change_auto_sending.filter(), state=RegStates.Gas_attribute_choose)
async def change_auto_sending(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
    await db.gasnn_set_attribute_account(account_id=callback_data.get('id'),
                                         attribute='auto_sending',
                                         value=bool(int(callback_data.get('auto_sending'))))
    answer = await bot.send_message(text='Готово!', chat_id=callback_q.message.chat.id)
    await bot.answer_callback_query(callback_q.id)
    await MainStates.MainMenuNavigation.set()
    await delete_message_with_timeout(answer, 2)
    await delete_message_with_timeout(callback_q.message, 0)


@dp.callback_query_handler(gasnn_change_increment_button.filter(), state=RegStates.Gas_attribute_choose)
async def change_increment(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):

    await db.gasnn_set_attribute_account(account_id=callback_data.get('id'),
                                         attribute='auto_sending',
                                         value=bool(callback_data.get('auto_sending')))

    default_increment = callback_data.get('default_increment', 0)
    message = await bot.send_message(
        chat_id=callback_q.message.chat.id,
        text='Введите новое значение (текущее значение: {}):'.format(default_increment))

    data = await state.get_data()
    data['message_for_delete'] = message
    await state.update_data(data)

    await callback_q.message.delete()

    await RegStates.Gas_default_increment_input.set()

    await bot.answer_callback_query(callback_q.id)


@dp.message_handler(state=RegStates.Gas_default_increment_input)
async def save_increment_input(message: Message, state: FSMContext):

    await MainStates.MainMenuNavigation.set()

    new_value = message.text

    try:
        new_value = float(new_value)
    except ValueError:
        answer = await message.answer(text='Введено некорректное значение!')
        await delete_message_with_timeout(answer, 2)

    data = await state.get_data()
    account_id = int(data.get('account_id', 0))

    if isinstance(new_value, float) \
            and isinstance(account_id, int) \
            and account_id != 0:

        await db.gasnn_set_attribute_account(account_id=account_id, attribute='default_increment', value=new_value)

        answer = await message.answer(text='Новое значение установлено!')
        await delete_message_with_timeout(answer, 2)

    await message.delete()

    message_for_delete = data.get('message_for_delete')
    if message_for_delete is not None and isinstance(message_for_delete, Message):
        await message_for_delete.delete()
        data['message_for_delete'] = None


@dp.callback_query_handler(gasnn_delete_account.filter(), state=RegStates.Gas_attribute_choose)
async def ask_before_delete_account(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):

    account_id = int(callback_data.get('id', 0))
    markup = await yes_no_keyboard(question_id='delete_gasnn_account', callback_data=str(account_id))
    account_info = await db.gasnn_get_account(account_id)
    text = 'Вы уверены, что хотите удалить ВСЮ информацию о лицевом счете "{}" ({})?'.format(account_info.get('name'),
                                                                                             account_info.get('login'))
    await bot.send_message(chat_id=callback_q.message.chat.id, text=text, reply_markup=markup)

    await RegStates.Gas_delete_account_confirmation.set()

    await callback_q.message.delete()

    await bot.answer_callback_query(callback_q.id)


@dp.callback_query_handler(yes_no_cbd.filter(question_id='delete_gasnn_account'),
                           state=RegStates.Gas_delete_account_confirmation)
async def delete_account_confirm(callback: CallbackQuery, callback_data: dict, state: FSMContext):

    deletion_confirmed = bool(int(callback_data.get('value', 0)))
    account_id = int(callback_data.get('callback_data', 0))

    data = await state.get_data()

    if deletion_confirmed:
        await db.gasnn_delete_account(account_id)
        message = await bot.send_message(chat_id=callback.message.chat.id,
                                         text='Аккаунт удалён!')
        await bot.answer_callback_query(callback.id)
        await delete_message_with_timeout(message, 2)

        main_menu_message_id = int(data.get('main_menu_message_id', 0))
        if main_menu_message_id != 0:
            markup = await select_operator_menu(operator=data.get('operator'),
                                                action=data.get('last_action'),
                                                user_id=callback.message.from_user.id,
                                                main_menu_message_id=main_menu_message_id)
            await bot.edit_message_reply_markup(message_id=main_menu_message_id,
                                                reply_markup=markup,
                                                chat_id=callback.message.chat.id)

    else:
        await bot.answer_callback_query(callback.id)

    await callback.message.delete()
    await MainStates.MainMenuNavigation.set()


@logger.catch()
@dp.callback_query_handler(gasnn_cancel.filter(), state=RegStates.Gas_attribute_choose)
async def ask_before_delete_account(callback_q: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.get_data()
    await MainStates.MainMenuNavigation.set()
    await callback_q.message.delete()
    await bot.answer_callback_query(callback_q.id)


@logger.catch()
@dp.message_handler(state=RegStates.Gas_attribute_choose)
@dp.message_handler(state=RegStates.Gas_delete_account_confirmation)
async def delete_wrong_message(message: Message, state: FSMContext):
    if message is not None\
            and isinstance(message, Message)\
            and not message.from_user.is_bot:
        await bot.delete_message(chat_id=state.chat, message_id=message.message_id)


