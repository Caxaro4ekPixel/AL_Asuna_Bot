"""
DEV TOOLS:
/id - отправить инфу о чате из БД
/add - добавляет пустой эпизод в БД
/log - скидывает лог в админский чат 
"""

import json
from aiogram import Router, html, Bot
from aiogram.types import Message, FSInputFile
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.filters.admins import AdminFilter
from aiogram.filters import Command, CommandObject
from asuna_bot.db.odm import Chat, Release, Episode, User
from asuna_bot.config import CONFIG, __logpath__
from datetime import datetime
import os
import asyncio
from asuna_bot.middlewares.database import UserMiddleware


dev_router = Router()
dev_router.message.filter(AdminFilter())
dev_router.message.middleware(UserMiddleware())
bot: Bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')


@dev_router.message(Command("id"))
async def send_chat_id(msg: Message):
    db_chat = await Chat.get_by_id(msg.chat.id)
    db_release = await Release.get_by_chat_id(msg.chat.id)
    await msg.delete()
    chat_obj = json.loads(db_chat.model_dump_json())
    chat_formatted_str = json.dumps(chat_obj, indent=2, ensure_ascii=False)

    release_obj = json.loads(db_release.model_dump_json())
    release_formatted_str = json.dumps(release_obj, indent=2, ensure_ascii=False)
    text = (
        f"<u>chat_name:</u> {html.code(msg.chat.full_name)}\n" \
        f"<u>chat_id:</u> {html.code(msg.chat.id)}\n" \
        f"<u>db_chat:</u> {html.code(chat_formatted_str)}\n" \
        f"<u>db_release:</u> {html.code(release_formatted_str)}\n"
    )
    await bot.send_message(CONFIG.bot.admin_chat, text)


@dev_router.message(Command("add"))
async def add_ep_to_release(msg: Message, command: CommandObject):
    ep_num = float(command.args)
    db_release = await Release.get_by_chat_id(msg.chat.id)
    new_ep = Episode(
        number=ep_num,
        status="test",
        date=datetime.now(),
        deadline_at=datetime.now()
    )
    await db.add_episode(db_release, new_ep)


@dev_router.message(Command("log"))
async def send_log_file(msg: Message):
    files = os.listdir(__logpath__)
    for file in files:
        await msg.answer_document(FSInputFile(__logpath__ + file))
        asyncio.sleep(1)


@dev_router.message(Command("test"))
async def test(msg: Message, db_user: User):
    await msg.answer(db_user.name)
    await msg.answer(str(db_user.role))
