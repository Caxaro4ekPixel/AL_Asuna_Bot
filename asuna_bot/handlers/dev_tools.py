"""
DEV TOOLS:
/id - отправить инфу о чате из БД
/add - добавляет пустой эпизод в БД
/log - скидывает лог в админский чат 
/announce - рассылает сообщение во все конфы-онгоинги
"""

import json
from aiogram import Router, html, Bot
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramRetryAfter
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.filters.admins import AdminFilter
from aiogram.filters import Command, CommandObject
from asuna_bot.db.odm import Chat, Release, Episode
from asuna_bot.config import CONFIG, __logpath__
from datetime import datetime
import os
import asyncio
from loguru import logger as log
from anilibria import AniLibriaClient

dev_router = Router()

dev_router.message.filter(AdminFilter())
bot: Bot = Bot(token=CONFIG.bot.token, parse_mode="HTML")


@dev_router.message(Command("id"))
async def send_chat_id(msg: Message):
    db_chat = await Chat.get_by_id(msg.chat.id)
    db_release = await Release.get_by_chat_id(msg.chat.id)

    if not db_chat or not db_release:
        log.error("dev_tools.py -> send_chat_id")
        log.error("Не найдено записи о чате или релизе в БД!")
        return
    
    try:
        await msg.delete()
    except Exception:
        pass
    

    chat_obj = json.loads(db_chat.model_dump_json())
    chat_formatted_str = json.dumps(chat_obj, indent=2, ensure_ascii=False)

    release_obj = json.loads(db_release.model_dump_json())
    release_formatted_str = json.dumps(release_obj, indent=2, ensure_ascii=False)
    text = (
        f"<u>chat_name:</u> {html.code(msg.chat.full_name)}\n"
        f"<u>chat_id:</u> {html.code(msg.chat.id)}\n"
        f"<u>db_chat:</u> {html.code(chat_formatted_str)}\n"
        f"<u>db_release:</u> {html.code(release_formatted_str)}\n"
    )
    await bot.send_message(CONFIG.bot.admin_chat, text)


@dev_router.message(Command("add"))
async def add_ep_to_release(msg: Message, command: CommandObject):
    ep_num = float(command.args)
    db_release = await Release.get_by_chat_id(msg.chat.id)
    new_ep = Episode(
        number=ep_num, status="test", date=datetime.now(), deadline_at=datetime.now()
    )
    await db.add_episode(db_release, new_ep)


@dev_router.message(Command("log"))
async def send_log_file(msg: Message):
    files = os.listdir(__logpath__)
    for file in files:
        await msg.answer_document(FSInputFile(__logpath__ + file))
        await asyncio.sleep(1)


@dev_router.message(Command("announce"))
async def send_announce(msg: Message, command: CommandObject):
    chats = await Chat.get_all_ongoing_chats()
    text = msg.html_text.removeprefix("/announce").strip()
    if not command.text:
        return
    
    await msg.answer("Всего чатов-онгоингов: " + str(len(chats)))
    for chat in chats:
        try:
            await bot.send_message(chat.id, text + str(chat.id))
            await asyncio.sleep(1.1)
        except TelegramRetryAfter:
            await msg.answer("hitting limits!")
            continue
    await msg.answer("Рассылка закончена")



@dev_router.message(Command("update_ongoings"))
async def update_ongoings(msg: Message, command: CommandObject):
    chats = await Chat.get_all_ongoing_chats()
    al_client = AniLibriaClient()

    for chat in chats:
        title = await al_client.get_title(chat.release.id)
        # code 2 = завершен, code 1 = в работе
        if title.status.code == 2:
            text = html.code(title.id) + "\nЗавершен, но статус не изменен в ДБ"
            await bot.send_message(CONFIG.bot.admin_chat, text)
            await asyncio.sleep(3)