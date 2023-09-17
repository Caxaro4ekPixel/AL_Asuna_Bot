from typing import Optional, Dict, List
from beanie import Document, Link
from .episode import Episode
from .user import User

class Release(Document):
    id           : int
    chat_id      : int
    status       : Optional[str]
    code         : str
    en_title     : str
    ru_title     : str
    total_ep     : Optional[int]
    season       : Optional[Dict]
    is_ongoing   : bool = False
    is_top       : bool = False
    is_commer    : bool = False
    days_to_work : Optional[int] = 4
    team         : Optional[List[Link[User]]]
    episodes     : Optional[Dict[str, Episode]]
    
    class Settings:
        name = "releases"