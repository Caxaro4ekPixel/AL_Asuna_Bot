import asyncio
from aiogram import Bot, Dispatcher
from asuna_bot.handlers import __routers__
from asuna_bot.config import CONFIG
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from asuna_bot.db.odm import __beanie_models__
from beanie import init_beanie

from asuna_bot.api import ApiRssObserver


async def bot_coro() -> None:
    dp = Dispatcher()
    dp.include_routers(*__routers__)

    bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')
    await dp.start_polling(bot)


async def rss_coro() -> None:
    client = AsyncIOMotorClient(CONFIG.db.connection_string)
    db = getattr(client, CONFIG.db.db_name)
    await init_beanie(database=db, document_models=__beanie_models__)

    rss = ApiRssObserver()
    await rss.start_polling()


if __name__ == "__main__":
    logger.add("log.txt")

    loop = asyncio.get_event_loop()
    gather = asyncio.gather(

        loop.create_task(bot_coro()),
        loop.create_task(rss_coro()),
    )
    loop.run_until_complete(gather)
