from typing import List, Optional
from beanie import Document
from pydantic import BaseModel
from beanie.operators import Set


class NyaaRssConf(BaseModel):
    running: bool = True
    interval: int = 120
    limit: int = 30
    last_id: int = 0
    submitters: List[str] = ["SubsPlease", "Erai-Raws"]
    exceptions: List[str] = ["HEVC"]
    base_url: str = "https://nyaa.si/"
    params: dict = {"page": "rss", "q": "", "c": "1_2", "f": "0"}


class AlApiConf(BaseModel):
    site_url: str = "https://www.anilibria.tv/release/"
    back_url: str = "https://backoffice.anilibria.top/resources/anime__releases/"
    last_update: int = 1695034197


class BotConfig(Document):
    timezone: str = "Europe/Moscow"
    deadline_fmt: str = "%d.%m  %H:%M"
    update_fmt: str = "%d дней %H Часов %M Минут"
    al_api: AlApiConf = AlApiConf()
    nyaa_rss: NyaaRssConf = NyaaRssConf()

    class Settings:
        name = "bot_config"

    @classmethod
    async def get_al_conf(cls) -> Optional["AlApiConf"]:
        conf = await cls.find_one({})
        return conf.al_api

    @classmethod
    async def get_nyaa_rss_conf(cls) -> Optional["NyaaRssConf"]:
        conf = await cls.find_one({})
        return conf.nyaa_rss

    @classmethod
    async def update_nyaa_rss_conf(cls, **kwargs) -> None:
        for key, val in kwargs.items():
            await cls.update(Set({f"nyaa_rss.{key}": val}))

    @classmethod
    async def update_al_api_conf(cls, **kwargs) -> None:
        for key, val in kwargs.items():
            await cls.update(Set({f"al_api.{key}": val}))
