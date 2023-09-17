"""
DEV TOOLS:
- отправить id чата
"""

from aiogram import Router, html
from aiogram.types import Message
from asuna_bot.filters.admins import AdminFilter
from aiogram.filters import Command

dev_router = Router()
dev_router.message.filter(AdminFilter())


@dev_router.message(Command("id"))
async def send_chat_id(msg: Message):
    await msg.reply(
        f"""
        chat_name: {html.code(msg.chat.full_name)}
        chat_id: {html.code(msg.chat.id)}
        user_id: {html.code(msg.from_user.id)}
        """
    )