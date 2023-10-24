from typing import List, Optional
from beanie import Document


class User(Document):
    id   : int
    name : str
    role : List[str]

    class Settings:
        name = "users"

    @classmethod
    async def get_by_id(cls, id: int) -> Optional["User"]:
        return await cls.find_one(cls.id == id)