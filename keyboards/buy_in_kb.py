from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

k_buy=InlineKeyboardButton(text='Открыть', callback_data='new_buy')
k_cancel = InlineKeyboardButton(text='Скрыть', callback_data='new_cancel')
k_delete = InlineKeyboardButton(text='Удалить', callback_data='new_delete')
kb_buy_in = InlineKeyboardMarkup(row_width=2).row(k_delete, k_cancel).row(k_buy)
