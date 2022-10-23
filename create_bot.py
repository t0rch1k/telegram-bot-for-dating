import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor



logging.basicConfig(level=logging.INFO)

bot = Bot(token="bot token")
dp = Dispatcher(bot, storage=MemoryStorage())


