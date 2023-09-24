from typing import List
from beanie import Document


class User(Document):
    id   : int
    name : str
    role : List[str]

    class Settings:
        name = "users"