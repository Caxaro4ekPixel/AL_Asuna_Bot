from typing import Optional
from pydantic import BaseModel, HttpUrl, AnyUrl
from datetime import datetime


class NyaaTorrent(BaseModel):
    # основные атрибуты торрента
    id: int
    submitter: Optional[str | None]
    serie: Optional[float | None]
    quality: Optional[str | None]
    url: HttpUrl
    file_url: HttpUrl
    magnet: AnyUrl
    size: str 
    title: str
    date: datetime

    # доп атрибуты, мб понадобятся где-нибудь
    is_hevc: bool
    full_title: str
    type: str
    category: str
    seeders: int
    leechers: int
    downloads: int