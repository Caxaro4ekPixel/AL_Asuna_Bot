from typing import List, Optional
from pydantic import BaseModel, HttpUrl, AnyUrl
from datetime import datetime
from beanie import Link
from .user import User


class Torrent(BaseModel):
    id: int
    submitter: str
    quality: str
    url: HttpUrl
    file_url: AnyUrl
    magnet: AnyUrl
    size: str
    title: str


class Episode(BaseModel):
    number: Optional[float]
    status: Optional[str]
    date: datetime
    deadline_at: datetime
    translation_time: Optional[int]
    voiceover_time: Optional[int]
    mix_time: Optional[int]
    fix_time: Optional[int]
    overall_time: Optional[int]
    uploaded_at: Optional[datetime]
    team: Optional[List[Link[User]]]
    torrents: List[Torrent]
