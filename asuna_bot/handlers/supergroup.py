"""
Хендлер для отлова миграции в супергруппу,
при выдаче прав боту с пунктом "Анонимность"
запустится логика команды /start
"""

from aiogram import Router, types, Bot
from asuna_bot.config import CONFIG
from asuna_bot.filters.supergroup import MigrateToSupergroup
from asuna_bot.handlers.start import search_title, send_title_to_chat
from asuna_bot.db.odm import Chat

supergroup_router = Router()


@supergroup_router.message(MigrateToSupergroup())
async def supergroup(message: types.Message):
    bot = Bot(token=CONFIG.bot.token)
    new_chat_id = message.migrate_to_chat_id
    await bot.send_message(new_chat_id, f"теперь это супергруппа, id={new_chat_id}")

    await Chat.add(new_chat_id, message.chat.full_name)

    titles = await search_title(message)
    await send_title_to_chat(titles, new_chat_id)
    del bot
