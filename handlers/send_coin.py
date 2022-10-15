from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import sql_db as sq
from keyboards import kb_client, kb_cancel
from handlers import client


class FSMSend(StatesGroup):
   amount = State()
   user_name = State()

# Начало перевода
async def send_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите сумму',reply_markup=kb_cancel)
    await FSMSend.amount.set()

# Получение суммы для перевода
async def get_amount(message: types.Message, state = FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    global amount
    try:
        amount=float(message.text)
        if amount<0.01:
            await message.answer('Минимальное значение составляет 0.01 coin🚫', reply_markup=kb_cancel)
            return
        if len(str(amount).split('.')[1])>2:
                await message.answer('Введите число, у которого количество знаков после точки меньше трех🚫', reply_markup=kb_cancel)
                return
    except:
        await message.answer('Введите число🚫', reply_markup=kb_cancel)
        return
    balance = await sq.sql_get_unflsfb(message.from_user.id)
    balance=float(balance[-1])
    if (balance >= amount):
        async with state.proxy() as data:
            data['amount'] = amount
        await message.answer('Напишите никнейм пользователя', reply_markup=kb_cancel)
        await FSMSend.next()
    else:
        await message.answer(f'На счету недостаточно средств.\nУ вас есть {balance} coin💎', reply_markup=kb_cancel)


# Получение username пользователя
async def get_user(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    if message.text[0] == '@': message.text = message.text[1:]
    if await sq.sql_check_payee(message.text):
        user=await sq.sql_get_unflsfb(message.from_user.id)
        user=user[1]
        if message.text==user:
            await message.answer('Нельзя осуществить перевод самому себе', reply_markup=kb_cancel)
        else:
            async with state.proxy() as data:
                data['user_name'] = message.text
            await FSMSend.next()
            await transfer(message,state)
    else:
        await message.answer('Такого пользователя нет', reply_markup=kb_cancel)
   
# Перевод
async def transfer(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await sq.sql_send_coin(message, state)
    await message.answer(f'Успешный перевод {amount} coin🎊',reply_markup=kb_client)
    await state.finish()


# Регистрация хендлеров
def register_handlers_send(dp: Dispatcher):
    dp.register_message_handler(send_start, lambda message: '💸Перевод' in message.text)
    dp.register_message_handler(get_amount, state=FSMSend.amount)
    dp.register_message_handler(get_user, state=FSMSend.user_name)
   

