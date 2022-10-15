from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base.sql_db import sql_change_name
from keyboards import kb_cancel, kb_client
from handlers import client


class FSM_change_name(StatesGroup):
    first_name = State()
    last_name = State()

# Начало изменения имени
async def change_name_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите новое имя', reply_markup=kb_cancel)
    await FSM_change_name.first_name.set()

# Изменение имени и запрос фамилии
async def get_first_name(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите новую фамилию', reply_markup=kb_cancel)
    async with state.proxy() as data:
        data['first_name'] = message.text.strip()
    await FSM_change_name.last_name.set()

# Изменение фамилии и сохранение изменений
async def get_last_name(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        data['last_name'] = message.text.strip()
        await sql_change_name(message.from_user.id, list(data.values()))
    await state.finish()
    await message.answer('Имя успешно изменено', reply_markup=kb_client)

# Регистрация хендлеров
def register_handlers_add_subscription(dp: Dispatcher):
    dp.register_message_handler(change_name_start, commands=['change_name'])
    dp.register_message_handler(get_first_name, state=FSM_change_name.first_name)
    dp.register_message_handler(get_last_name, state=FSM_change_name.last_name)
