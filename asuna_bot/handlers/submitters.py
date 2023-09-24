"""
Равки меняются по старинке, командой /raw 
В будущих обновлениях будет переработано
"""

from aiogram import Router, html
from aiogram.types import Message
from aiogram.filters import CommandObject, Command
from asuna_bot.filters.chat_type import ChatTypeFilter

from asuna_bot.db.mongo import Mongo as db

submitter_router = Router()
submitter_router.message.filter(Command("raw"), ChatTypeFilter("supergroup"))


@submitter_router.message()
async def change_submitter(msg: Message, command: CommandObject):
    if command.args is None:
        await msg.answer(html.italic("Укажите группу, например \n/raw [Erai-Raws]"))
    else:
        await db.update_chat_conf(msg.chat.id, submitter=command.args)
        await msg.answer(f"{command.args} установлена")
        # TODO добавлять равки в вайтлист

