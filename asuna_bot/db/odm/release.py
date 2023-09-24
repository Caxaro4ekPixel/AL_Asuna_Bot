from typing import Optional, Dict
from beanie import Document
from .episode import Episode


class Release(Document):
    id: int
    chat_id: int
    status: Optional[str]
    code: str
    en_title: str
    ru_title: str
    last_update: int = None
    is_ongoing: bool = True
    is_top: bool = False
    is_commer: bool = False
    days_to_work: Optional[int] = 4
    episodes: Optional[Dict[str, Episode]] = None

    class Settings:
        name = "releases"
        keep_nulls = False
