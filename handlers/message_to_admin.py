from create_bot import bot, adminList
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from keyboards import kb_cancel, kb_client, kb_reg
from handlers import client


class FSMText(StatesGroup):
    text = State()
   
# Предложение оставить сообщение
async def text_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    await message.answer('Оставьте свое сообщение', reply_markup=kb_cancel)
    await FSMText.text.set()

# Сохранение сообщения и отправка админам
async def send_text_to_admin(message: types.Message, state = FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    for admin in adminList:
        await bot.send_message(chat_id=admin, text=f'Пользователь @{message.from_user.username} отправил сообщение:\
            \n{message.text}')
    await state.finish()
    if (await client.check_user(message)):
        await message.answer('Ваше сообщение доставлено',reply_markup=kb_client)
    else:
        await message.answer('Ваше сообщение доставлено',reply_markup=kb_reg)
        

# Регистрация хендлеров
def register_handlers_message_admin(dp: Dispatcher):
    dp.register_message_handler(text_start, commands=['mes_admin'])
    dp.register_message_handler(send_text_to_admin, state=FSMText.text)
