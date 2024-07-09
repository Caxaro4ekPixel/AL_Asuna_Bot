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
    
    @classmethod
    async def get_all(cls) -> List["User"]:
        return await cls.find_all().to_list()
    
    @classmethod
    async def get_all_user_ids(cls) -> List:
        all_users = await cls.find_all().to_list()
        return [user.id for user in all_users]