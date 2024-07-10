"""
Командой /time сверяем за сколько вышла серия с момента появления на торрентах

"""

from aiogram import Router, types, html
from aiogram.filters import Command
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.chat_type import ChatTypeFilter
from asuna_bot.db.odm import Release
from asuna_bot.utils import craft_time_str
from anilibria import AniLibriaClient
from loguru import logger as log


libria = AniLibriaClient()
time_router = Router()
time_router.message.filter(AllowedUserFilter(), Command("time"))


@time_router.message(ChatTypeFilter(chat_type="supergroup"))
async def cmd_time(message: types.Message):
    release = await Release.get_by_chat_id(message.chat.id)
    title = await libria.get_title(release.id)
    log.info(f"Checking time for {title}")
    td = await release.check_time(title)
    time = craft_time_str(td)
    if td:
        await message.answer(
                f"{title.player.episodes.last}-я серия вышла за:\n{html.bold(time)}"
            )
    else:
        await message.answer("Неудалось засечь время для последнего эпизода :(")