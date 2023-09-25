"""
Командой /time сверяем за сколько вышла серия с момента появления на торрентах

"""

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.chat_type import ChatTypeFilter

from anilibria import AniLibriaClient
from asuna_bot.api import ApiRssObserver

libria = AniLibriaClient()
observer = ApiRssObserver()
settings_router = Router()
settings_router.message.filter(AllowedUserFilter())


@settings_router.message(ChatTypeFilter(chat_type="supergroup"), Command("deadline"))
async def cmd_deadline(message: types.Message, command: CommandObject):
    chat_controller = observer.chats.get(message.chat.id)
    if command.args.isdigit():
        chat_controller._release.days_to_work = int(command.args)
        await chat_controller._release.save()
        await message.answer(f"Установлен дедлайн в {command.args} дня")