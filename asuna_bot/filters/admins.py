from aiogram.filters import Filter
from aiogram.types import Message
from asuna_bot.db.odm import User
from asuna_bot.config import CONFIG


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in CONFIG.bot.admin_ids:
            return True
        return False


class AllowedUserFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        all_users = await User.get_all_user_ids()
        return message.from_user.id in all_users

