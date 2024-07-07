"""
Ботом могут пользоваться только зарегистрированные пользователи.
Регистрация происходит путем пересылки админом любого сообщения пользователя,
если настройки приватности не позволяют добавить пользователя,
просим на время изменить настройки приватности.
"""

from aiogram import Router
from aiogram.types import Message
from asuna_bot.filters.admins import AdminFilter

from asuna_bot.filters.chat_type import ChatTypeFilter

admin_router = Router()
admin_router.message.filter(AdminFilter(), ChatTypeFilter("private"))


@admin_router.message()
async def accept_user(msg: Message):
    if msg.forward_from:
        user_id = msg.forward_from.id

        await msg.answer(f"Выберите роль для {user_id}")
        # TODO кнопки с ролями
        # await db.add_user(user_id)
        return

    if msg.forward_sender_name:
        name = msg.forward_sender_name
        await msg.answer(f"Не могу добавить {name} из-за настроек приватности 😔")
