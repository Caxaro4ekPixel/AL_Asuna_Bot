from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from beanie import Link
from .user import User


class Episode(BaseModel):
    number: Optional[float] = None
    status: Optional[str] = "Перевод"
    date: datetime
    deadline_at: datetime
    translation_time: Optional[int] = 0
    voiceover_time: Optional[int] = 0
    mix_time: Optional[int] = 0
    fix_time: Optional[int] = 0
    overall_time: Optional[int] = 0
    uploaded_at: Optional[datetime] = 0
    team: Optional[List[Link[User]]] = []
