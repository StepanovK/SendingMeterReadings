from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
import database.commands as db

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State
from .navigation import clear_message, delete_message_with_timeout, MainStates


class RegStates(StatesGroup):
    InputName = State()
    InputPhone = State()
    InputEmail = State()
    EndInput = State()


@dp.callback_query_handler(text='start_registration', state=MainStates.MainMenuNavigation)
@dp.callback_query_handler(text='start_registration', state=RegStates.EndInput)
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    await RegStates.InputName.set()
    data = {'first_name': '', 'phone': '', 'email': '', 'messages_id_for_delete': []}
    data['messages_id_for_delete'].append(callback.message.message_id)
    new_message = await bot.send_message(text='Введите ваше имя',
                                         chat_id=callback.message.chat.id,
                                         disable_notification=True)
    data['messages_id_for_delete'].append(new_message.message_id)
    await state.update_data(data)


@dp.message_handler(state=RegStates.InputName)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['first_name'] = message.text
    data['messages_id_for_delete'].append(message.message_id)
    new_message = await message.answer(text='Введите ваш номер телефона в формате 89101234567')
    await clear_message(chat_id=message.chat.id, messages_id=data['messages_id_for_delete'])
    data['messages_id_for_delete'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.InputPhone.set()


@dp.message_handler(state=RegStates.InputPhone)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['phone'] = message.text
    await state.update_data(data)
    data['messages_id_for_delete'].append(message.message_id)
    new_message = await message.answer(text='Введите ваш e-mail адрес для уведомлений')
    await clear_message(chat_id=message.chat.id, messages_id=data['messages_id_for_delete'])
    data['messages_id_for_delete'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.InputEmail.set()


@dp.message_handler(state=RegStates.InputEmail)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['email'] = message.text
    data['messages_id_for_delete'].append(message.message_id)
    text = 'Вы ввели следующие данные: \nИмя: {}\nтел.: {}\nemail: {}'.format(data['first_name'],
                                                                              data['phone'],
                                                                              data['email'])
    new_message = await message.answer(text=text, reply_markup=confirm_keyboard())
    await clear_message(chat_id=message.chat.id, messages_id=data['messages_id_for_delete'])
    # data['messages_id_for_delete'].append(new_message.message_id)
    await state.update_data(data)
    await RegStates.EndInput.set()


def confirm_keyboard():
    markup = Markup()
    confirm_button = Button(text='Подтвердить', callback_data='confirm_registration')
    markup.add(confirm_button)
    repeat_button = Button(text='Повторить', callback_data='start_registration')
    markup.add(repeat_button)
    cancel_button = Button(text='Отмена', callback_data='start')
    markup.add(cancel_button)
    return markup


@dp.callback_query_handler(text='start', state=RegStates.EndInput)
async def start_work(callback: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await bot.send_message(text='Нажмите команду /start', chat_id=callback.message.chat.id)
    await bot.answer_callback_query(callback.id)


@dp.callback_query_handler(text='confirm_registration', state=RegStates.EndInput)
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await clear_message(chat_id=callback.message.chat.id, messages_id=data['messages_id_for_delete'])
    data['id'] = callback.message.chat.id
    username = callback.message.chat.username
    username = callback.message.chat.full_name if username is None else username
    data['username'] = username
    await db.add_user_info(data)
    await state.reset_state()
    text = 'Отлично, {}!\nНажмите команду /start для начала работы'.format(data.get('first_name'))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    message = await bot.send_message(text=text, chat_id=callback.message.chat.id)
    await bot.answer_callback_query(callback.id)
    await delete_message_with_timeout(message, 5)
