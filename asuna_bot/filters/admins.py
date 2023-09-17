from aiogram.filters import Filter
from aiogram.types import Message
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.config import CONFIG


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in CONFIG.bot.admin_ids:
            return True
        return False


class AllowedUserFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        all_users = await db.get_all_user_ids()
        if message.from_user.id in all_users:
            return True
        return False