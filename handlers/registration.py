from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from aiogram.dispatcher.filters.state import StatesGroup, State


class RegStates(StatesGroup):
    InputName = State()
    InputPhone = State()
    InputEmail = State()


@dp.callback_query_handler(text='start_registration', state=None)
async def start_registration(callback: CallbackQuery, state: FSMContext):
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
    await message.answer(text='Вы ввели следующие данные: \nИмя: {}\nтел.: {}\nemail: {}'.format(data['first_name'],
                                                                                                 data['phone'],
                                                                                                 data['email']))
    await RegStates.InputEmail.set()
    await state.reset_state()
