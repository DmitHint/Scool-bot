from aiogram.utils import executor
from create_bot import dp
from data_base import sql_db as sq
from handlers import *


async def on_startup(_):
    print('Бот вышел в онлайн')
    sq.sql_start()

# Режим регистрации пользователя и обработка команды "Отмена"
registration.register_handlers_registration(dp) 

# Режим загрузки материалов
load.register_handlers_load(dp)

# Написать и отправить сообщения админу
message_to_admin.register_handlers_message_admin(dp)

# Написать и отправить сообщения пользователю
message_to_user.register_handlers_message_to_user(dp)

# Добавить один класс в подписки
add_subscription.register_handlers_add_subscription(dp)

# Изменить имя
change_name.register_handlers_add_subscription(dp)

# Удалить один класс из подписок
delete_subscription.register_handlers_delete_subscription(dp)

# Перевод монет между пользователями
send_coin.register_handlers_send(dp)

# Основные команды
client.register_handlers_client(dp)

if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

