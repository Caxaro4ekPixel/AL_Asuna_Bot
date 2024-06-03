"""
Report
формирует отчет по релизам
"""

from typing import List
from aiogram import Router, Bot, html
from aiogram.types import Message
from asuna_bot.filters.admins import AdminFilter
from aiogram.filters import Command
from asuna_bot.db.odm import Release
from asuna_bot.config import CONFIG
from asuna_bot.middlewares.database import UserMiddleware


report_router = Router()
report_router.message.filter(AdminFilter())
report_router.message.middleware(UserMiddleware())
bot: Bot = Bot(token=CONFIG.bot.token, parse_mode="HTML")


@report_router.message(Command("report"))
async def send_report(msg: Message):
    text = []
    ongoings: List[Release] = await Release.get_all_ongoings()
    for ongoing in ongoings:
        title = ongoing.ru_title
        ep_count = len(ongoing.episodes)

        if ep_count > 0:
            ikeys = [int(float(k)) for k in ongoing.episodes.keys()]
            episode = ongoing.episodes.get(str(max(ikeys)))
            status = episode.status

            text += [
                html.underline(html.bold(title)),
                f"{episode.number}-я серия {html.bold(status)}",
                "",
            ]

        else:
            pass
    await msg.answer("\n".join(text).replace(".0", ""))
