import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from middlewares import UsernameCacheMiddleware
from handlers import ranks, moderation, report, people, help

logging.basicConfig(level=logging.INFO)


async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(UsernameCacheMiddleware())

    dp.include_router(ranks.router)
    dp.include_router(moderation.router)
    dp.include_router(report.router)
    dp.include_router(people.router)
    dp.include_router(help.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
