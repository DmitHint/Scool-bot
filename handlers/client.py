from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_reg, kb_client, kb_cancel
from data_base import sql_db
from create_bot import adminList
from handlers.registration import cancel_handler
from aiogram.dispatcher import FSMContext

# Запись полученных сообщений
async def write_history(id, username, message):
    with open('history.txt', 'a', encoding="UTF-8") as f:
        if username is None: username = 'None'
        f.write(str(id) + '  ' + username + ' : ' + str(message) + '\n')

# Проверка регистрации у пользователя
async def check_user(message: types.Message, state = 0):
    data = await sql_db.sql_get_unflsfb(message.from_user.id)
    reply_markup = kb_reg if data is None else kb_client
    if state != 0: await state.finish()
    if not message.from_user.username:
        await message.answer(
            'Для дальнейшей работы придумайте и напишите, пожалуйста, имя пользователя в своем профиле telegram.',
            reply_markup=reply_markup)
        return False
    if data is None:
        await message.answer('Вы не зарегистрированы', reply_markup=reply_markup)
        return False
    else:
        if message.from_user.username != data[1]:
            await sql_db.sql_update_username(data[0], message.from_user.username)
    return True


# Обработка сообщений, тип которых можно добавить в базу данных
async def load_warning(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message )): return
    await message.reply('Используйте режим "🚀Загрузить"', reply_markup=kb_client)


# Обработка сообщений, тип которых не поддерживается
async def unsupported_types_warning(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await message.reply('Этот тип данных не поддерживается', reply_markup=kb_client)


# Отправка сообщения с функциями бота
async def fhelp(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await message.answer('/help - отображение всех функций\n\nКнопки:\n"🔔Новенькое" - отображение последних добавленных материалов из Ваших подписок\
    \n"🚀Загрузить" - загрузить материал\n"👤Профиль" - отображение информации об аккаунте\n"💸Перевод" - перевод монет другому человеку\
    \n\n/show_subs - показать классы в подписках\n/new_sub - подписаться на какой-то класс\
    \n/delete_sub - отписаться от какого-то класса\n/change_name - изменить имя\n/mes_admin - отправить сообщение админу\
    \n/balance - отображение баланса на счету\n/complain - пожаловаться на нарушение\n/delete_user - удалить свою учетную запись\
    \n/donate - поддержать разработчика (вознаграждается монетами)',
                         reply_markup=kb_client)


# Отобразить баланс пользователя
async def show_balance(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    data = await sql_db.sql_get_unflsfb(message.from_user.id)
    await message.answer(f'На счету: @{data[1]}\n{data[-1]} coin💎', reply_markup=kb_client)


# Отобразить баланс пользователя
async def show_account(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message )): return
    data = await sql_db.sql_get_unflsfb(message.from_user.id)
    username = '@' + data[1]
    await message.answer(
        f'Никнейм: *{username}*\nИмя: *{data[2]}*\nФамилия: *{data[3]}*\nКласс: *{data[5]}*\nБаланс: *{data[-1]}* coin💎',
        reply_markup=kb_client, parse_mode=types.ParseMode.MARKDOWN)


# Удаление учетной записи пользователя
async def del_user(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await sql_db.sql_delete_user(message.from_user.id)
    await message.answer('Учетная запись удалена', reply_markup=kb_reg)


# Отображение подписок пользователя
async def show_subscriptions(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await bot.send_message(message.from_user.id, await sql_db.sql_show_subscriptions(message))


# Отправить материал пользователю при нажатии на кнопку
async def show_mat(callback: types.CallbackQuery):
    if not (await check_user(callback)): return
    b = float((await sql_db.sql_get_unflsfb(callback.message.chat['id']))[-1])
    row_id = ''
    for i in callback.message.text[::-1]:
        if i == '#':
            break
        row_id += i
    row_id = row_id[::-1]
    price = float(await sql_db.sql_get_price(row_id))
    if b < price:
        await callback.answer('На счету недостаточно средств', reply_markup=kb_client)
    else:
        await sql_db.sql_show_material(callback, row_id)
        await callback.answer()


# Удалить предложенный материал при нажатии на кнопку
async def hide_mat(callback: types.CallbackQuery):
    if not (await check_user(callback)): return
    await bot.delete_message(callback.message.chat['id'], callback.message.message_id)
    await callback.answer()


# Удалить из предлагаемых материалов для пользователя
async def del_mat(callback: types.CallbackQuery):
    if not (await check_user(callback)): return
    b = float((await sql_db.sql_get_unflsfb(callback.message.chat['id']))[-1])
    row_id = ''
    for i in callback.message.text[::-1]:
        if i == '#':
            break
        row_id += i
    row_id = row_id[::-1]
    await sql_db.sql_del_material(callback, row_id)
    await bot.delete_message(callback.message.chat['id'], callback.message.message_id)
    await callback.answer()

# Ответ на неправильную команду и текст
async def get_no_messages(message=types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await message.answer('Не понимаю, что это значит🚫', reply_markup=kb_client)


# Считывание материалов и отправка предварительных сведений о них пользователю
async def read_materials(message: types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await sql_db.sql_read_materials(message)


# Поддержка разработчика и начисление баллов
async def donate(message: types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await message.answer('Благодарю Вас за желание поддержать мой труд😊')
    await message.answer('https://yoomoney.ru/to/4100116978687558', disable_web_page_preview=True)


# Отправить жалобу на материал
async def complain(message: types.Message):
    await write_history(message.from_user.id, message.from_user.username, message.text)
    if not (await check_user(message)): return
    await message.answer('Функция в разработке')
    await message.answer('Очевидно, что нарушения будут происходить. Бот будет собирать количество жалоб на пользователя и удалять\
    пользователей, превысивших лимит. Возникает трудность в проверке обоснованности жалоб.\nЕсть вариант решения проблемы:\
    \nСоздать "отряд" проверенных пользователей, которые будут проверять жалобы других пользователей и получать вознаграждение.\
    \nВы можете оставить свое мнение или поделиться идеей с помощью /mes_admin', reply_markup=kb_client)


# Регистрация хендлеров
def register_handlers_client(dp=Dispatcher):
    dp.register_message_handler(fhelp, commands=['help'])
    dp.register_message_handler(del_user, commands=['delete_user'])
    dp.register_message_handler(donate, commands=['donate'])
    dp.register_message_handler(complain, commands=['complain'])
    dp.register_message_handler(show_balance, commands=['balance'])
    dp.register_message_handler(show_balance, lambda message: '💎Баланс' in message.text)
    dp.register_message_handler(show_account, lambda message: '👤Профиль' in message.text)
    dp.register_message_handler(read_materials, lambda message: '🔔Новенькое' in message.text)
    dp.register_message_handler(show_subscriptions, commands=['show_subs'])
    dp.register_callback_query_handler(show_mat, text='new_buy')
    dp.register_callback_query_handler(hide_mat, text='new_cancel')
    dp.register_callback_query_handler(del_mat, text='new_delete')
    dp.register_message_handler(load_warning, content_types=['photo', 'document', 'voice'])
    dp.register_message_handler(get_no_messages, content_types=['text', 'sticker'])
    dp.register_message_handler(unsupported_types_warning,
                                content_types=['music', 'audio', 'video_note', 'location', 'contact', 'venue'])
