"""
Командой /time сверяем за сколько вышла серия с момента появления на торрентах

"""

from aiogram import Router, types
from aiogram.filters import Command
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.chat_type import ChatTypeFilter

from anilibria import AniLibriaClient
from asuna_bot.api import ApiRssObserver

libria = AniLibriaClient()
observer = ApiRssObserver()
time_router = Router()
time_router.message.filter(AllowedUserFilter(), Command("time"))


@time_router.message(ChatTypeFilter(chat_type="supergroup"))
async def cmd_time(message: types.Message):
    chat_controller = observer.chats.get(message.chat.id)

    title = await libria.get_title(chat_controller._release.id)
    td = await chat_controller.check_time(title)
    if td:
        await message.answer(
                f"{title.player.episodes.last}-я серия вышла за:\n"
                f"{td.days} дней, {td.seconds // 3600} часов {(td.seconds//60)%60} минут"
            )
    else:
        await message.answer("Неудалось засечь время для последнего эпизода :(")