from aiogram.filters import Filter
from aiogram.types import Message
from asuna_bot.db.odm import User

class RoleFilter(Filter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message) -> bool:
        user = await User.get_by_id(message.from_user.id)
        
        if self.role in user.role:
            return True
        return False
