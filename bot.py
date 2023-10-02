import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from asuna_bot.handlers import __routers__
from asuna_bot.config import CONFIG
from motor.motor_asyncio import AsyncIOMotorClient
from asuna_bot.db.odm import __beanie_models__
from beanie import init_beanie
from asuna_bot.api import ApiRssObserver
from asuna_bot.utils.logging import set_logging



async def bot_coro() -> None:
    dp = Dispatcher()
    dp.include_routers(*__routers__)
    commands = [
        BotCommand(command="raw", description="Какую равки скидывать?: /raw [SubsPlease] (Erai-raws поумолчанию)"),
        BotCommand(command="srt", description="реплаем на файл сабов в формате .ass (Конвертирует .ass в .srt)"),
        BotCommand(command="deadline", description="Сколько дней до дедлайна? отображается в сообщении с торрентами (4 поумолчанию)"),
        BotCommand(command="time", description="Проверить за сколько вышла последняя серия"),
    ]
    bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')

    await bot.set_my_commands(commands)
    await dp.start_polling(bot)


async def rss_coro() -> None:
    client = AsyncIOMotorClient(CONFIG.db.connection_string)
    db = getattr(client, CONFIG.db.db_name)
    await init_beanie(database=db, document_models=__beanie_models__)

    rss = ApiRssObserver()
    await rss.start_polling()


if __name__ == "__main__":
    set_logging()

    loop = asyncio.get_event_loop()
    gather = asyncio.gather(

        loop.create_task(bot_coro()),
        loop.create_task(rss_coro()),
    )
    loop.run_until_complete(gather)
