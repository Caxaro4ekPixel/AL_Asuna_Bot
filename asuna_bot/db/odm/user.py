from typing import List, Optional
from beanie import Document


class User(Document):
    id        : int
    full_name : str
    username  : Optional[str]
    al_name   : Optional[str] = None
    role      : List[str]

    class Settings:
        name = "users"