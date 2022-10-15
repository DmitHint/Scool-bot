from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Token, adminList
import os

storage = MemoryStorage()
bot = Bot(token=Token)
dp = Dispatcher(bot, storage=storage)