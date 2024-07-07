"""
AUTOSTAGE:

"""

from aiogram import Router, F
from aiogram.types import Message
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.roles import RoleFilter



ASS = F.document.file_name.endswith("ass")
RAR = F.document.file_name.endswith("rar")
ZIP = F.document.file_name.endswith("zip")
MKV = F.document.file_name.endswith("mkv")
FLAC = F.audio.file_name.endswith("flac")
WAV = F.document.file_name.endswith("wav")
FIX = F.text.lower().contains("#фикс")


stage_router = Router()
stage_router.message.filter(AllowedUserFilter())

@stage_router.message(RoleFilter(role="войсер"), FLAC | WAV | RAR | ZIP)
async def test1(msg: Message):
    await msg.answer("Скинули дорогу")


@stage_router.message(RoleFilter(role="технарь"), FIX)
async def test(msg: Message):
    await msg.answer("скинули фиксы")


@stage_router.message(RoleFilter(role="переводчик"), ASS)
async def test2(msg: Message):
    await msg.answer("Скинули саб")


@stage_router.message(RoleFilter(role="оформитель"), RAR | ZIP | MKV)
async def test2(msg: Message):
    await msg.answer("Скинули оформу")