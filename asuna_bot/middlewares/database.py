from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from asuna_bot.db.odm import User


class UserMiddleware(BaseMiddleware):
    async def __call__(self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['db_user'] = await User.get_by_id(event.from_user.id)
        return await handler(event, data)
