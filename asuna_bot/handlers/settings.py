"""
Командой /deadline устанавливаем дедлайн
Командой /raw устанавливаем равку

"""

from aiogram import Router, types, html
from aiogram.filters import Command, CommandObject
from asuna_bot.db.odm import Release, Chat
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.chat_type import ChatTypeFilter
from loguru import logger


settings_router = Router()
settings_router.message.filter(AllowedUserFilter(), ChatTypeFilter("supergroup"))


@settings_router.message(Command("deadline"))
async def set_deadline(message: types.Message, command: CommandObject):
    if command.args:
        if command.args.isdigit():
            try:
                await Release.set_deadline(message.chat.id, int(command.args))
                await message.answer(f"Установлен дедлайн в {command.args} дня")
            except Exception as ex:
                logger.error("Не смогли установить дедлайн")
                logger.error(ex)
    else:
        pass


@settings_router.message(Command("raw"))
async def set_submitter(msg: types.Message, command: CommandObject):
    if command.args is None:
        await msg.answer(html.italic("Укажите группу, например \n/raw [Erai-Raws]"))
    else:
        await Chat.change_settings(msg.chat.id, "submitter", command.args)
