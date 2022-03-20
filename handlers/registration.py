from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup
import database.commands as db

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State


class RegStates(StatesGroup):
    InputName = State()
    InputPhone = State()
    InputEmail = State()


@dp.callback_query_handler(text='start_registration', state=None)
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await state.reset_state()
    data = {'first_name': '', 'phone': '', 'email': ''}
    await state.update_data(data)
    await bot.send_message(text='Введите ваше имя', chat_id=callback.from_user.id, disable_notification=True)
    await RegStates.InputName.set()


@dp.message_handler(state=RegStates.InputName)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['first_name'] = message.text
    await state.update_data(data)
    await message.answer(text='Введите ваш номер телефона в формате 89101234567')
    await RegStates.InputPhone.set()


@dp.message_handler(state=RegStates.InputPhone)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['phone'] = message.text
    await state.update_data(data)
    await message.answer(text='Введите ваш e-mail адрес для уведомлений')
    await RegStates.InputEmail.set()


@dp.message_handler(state=RegStates.InputEmail)
async def start_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    data['email'] = message.text
    await state.update_data(data)
    await state.reset_state(with_data=False)
    await message.answer(text='Вы ввели следующие данные: \nИмя: {}\nтел.: {}\nemail: {}'.format(data['first_name'],
                                                                                                 data['phone'],
                                                                                                 data['email']),
                         reply_markup=confirm_keyboard())


def confirm_keyboard():
    markup = Markup()
    confirm_button = Button(text='Подтвердить', callback_data='confirm_registration')
    markup.add(confirm_button)
    repeat_button = Button(text='Повторить', callback_data='start_registration')
    markup.add(repeat_button)
    cancel_button = Button(text='Отмена', callback_data='start')
    markup.add(cancel_button)
    return markup


@dp.callback_query_handler(text='start')
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await bot.send_message(text='Нажмите команду /start', chat_id=callback.from_user.id)


@dp.callback_query_handler(text='confirm_registration')
async def start_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['id'] = callback.from_user.id
    data['username'] = callback.from_user.username
    await db.add_user_info(data)
    await state.reset_state()
    text = 'Отлично, {}! \n Нажмите команду /start для начала работы'.format(data.get('first_name'))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await bot.send_message(text=text, chat_id=callback.from_user.id)
