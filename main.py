import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from db import init_db
from handl_start import router as start_router
from handl_register import router as register_router
from handl_chat import router as chat_router
from handl_group import router as group_router

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN mavjud emas.")

    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(register_router)
    dp.include_router(chat_router)
    dp.include_router(group_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
