from create_bot import bot, adminList
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from keyboards import kb_cancel, kb_client
from handlers import client


class FSMTextUser(StatesGroup):
    user=State()
    text = State()

# Запрос id пользователя, которому нужно отправить сообщение
async def find_user(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите id пользователя', reply_markup=kb_cancel)
    await FSMTextUser.user.set()
    
# Предложение оставить сообщение
async def text_to_user_start(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        data['user']=message.text
    await message.answer('Оставьте свое сообщение', reply_markup=kb_cancel)
    await FSMTextUser.text.set()

# Сохранение сообщения и отправка пользователю
async def send_text_to_user(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        user_id=data['user']
    await bot.send_message(chat_id=user_id, text=f'Админ отправил вам сообщение:\
        \n{message.text}')
    await message.answer('Ваше сообщение доставлено',reply_markup=kb_client)
    await state.finish()

# Регистрация хендлеров
def register_handlers_message_to_user(dp: Dispatcher):
    dp.register_message_handler(find_user, commands=['mes_user'])
    dp.register_message_handler(text_to_user_start, state=FSMTextUser.user)
    dp.register_message_handler(send_text_to_user, state=FSMTextUser.text)