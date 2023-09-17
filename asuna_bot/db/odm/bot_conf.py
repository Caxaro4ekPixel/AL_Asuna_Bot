from typing import List
from beanie import Document
from pydantic import BaseModel

class NyaaRssConf(BaseModel):
    running    : bool = True
    interval   : int = 120
    limit      : int = 30
    last_id    : int = 0
    submitters : List[str] = ["SubsPlease", "Erai-Raws"]
    exceptions : List[str] = ["HEVC"]
    base_url   : str = "https://nyaa.si/"
    params     : dict = {"page": "rss", "q": "", "c": "1_2", "f": "0"}

class BotConfig(Document):
    timezone : str = "Europe/Moscow"
    nyaa_rss : NyaaRssConf = NyaaRssConf()

    class Settings:
        name = "bot_config"
