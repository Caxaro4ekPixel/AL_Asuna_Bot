import asyncio
from aiogram import Bot, Dispatcher
from asuna_bot.handlers import __routers__
from asuna_bot.config import CONFIG

from motor.motor_asyncio import AsyncIOMotorClient
from asuna_bot.db.odm import __beanie_models__
from beanie import init_beanie

from asuna_bot.api import WsRssObserver
from asuna_bot.main.anilibria_client import al_client


async def migration() -> None:
    from migration import create_chat_list, create_release_list, create_user_list
    from asuna_bot.db.odm import Chat, Release, User, BotConfig
    client = AsyncIOMotorClient(CONFIG.db.connection_string)
    test = getattr(client, CONFIG.db.db_name)
    await init_beanie(database=test, document_models=__beanie_models__)
    # await User.insert_many(create_user_list())
    await Release.insert_many(create_release_list())
    # await Chat.insert_many(create_chat_list())
    # conf = BotConfig()
    # await BotConfig.insert(conf)


async def bot_coro() -> None:
    # await migration()

    dp = Dispatcher()
    dp.include_routers(*__routers__)

    bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')
    await dp.start_polling(bot)


async def rss_coro() -> None:
    client = AsyncIOMotorClient(CONFIG.db.connection_string)
    db = getattr(client, CONFIG.db.db_name)
    await init_beanie(database=db, document_models=__beanie_models__)

    rss = WsRssObserver()
    await rss.start_polling()


if __name__ == "__main__":
    from asuna_bot.utils import logging

    logging.setup()

    loop = asyncio.get_event_loop()

    gather = asyncio.gather(
        loop.create_task(al_client.astart()),
        loop.create_task(bot_coro()),
        loop.create_task(rss_coro()),
    )
    loop.run_until_complete(gather)

    # task1 = asyncio.ensure_future(bot_coro())
    # task2 = asyncio.ensure_future(rss_coro())
    # task3 = asyncio.ensure_future(al_client.astart())
    # loop.run_until_complete(asyncio.gather(task1, task2, task3))
