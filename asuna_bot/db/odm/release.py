from datetime import datetime, timedelta
from typing import Optional, Dict, List
from beanie import Document
from loguru import logger as log
from .episode import Episode
from anilibria import Title
from beanie.operators import Set

class Release(Document):
    id: int
    chat_id: int
    status: Optional[str] = ""
    code: str
    en_title: str
    ru_title: str
    is_ongoing: bool = True
    is_top: bool = False
    is_commer: bool = False
    days_to_work: Optional[int] = 4
    episodes: Optional[Dict[str, Episode]] = {}

    class Settings:
        name = "releases"

    @classmethod
    async def get_by_id(cls, id: int) -> Optional["Release"]:
        return await cls.find_one(cls.id == id)
    
    @classmethod
    async def get_by_chat_id(cls, chat_id: int) -> Optional["Release"]:
        return await cls.find_one(cls.chat_id == chat_id)
    
    @classmethod
    async def get_by_code(cls, code: str) -> Optional["Release"]:
        return await cls.find_one(cls.code == code)
    
    @classmethod
    async def get_all_ongoings(cls) -> Optional[List["Release"]]:
        try:
            return await cls.find(cls.is_ongoing == True,  # noqa: E712
                                   fetch_links=True).to_list()
        except Exception as ex:
            log.error("DB problem!")
            log.error(ex)

    @classmethod
    async def get_all_tops(cls) -> Optional[List["Release"]]:
        try:
            return await cls.find(cls.is_top == True,  # noqa: E712
                                   fetch_links=True).to_list()
        except Exception as ex:
            log.error("DB problem!")
            log.error(ex)

    @staticmethod
    async def add_episode(cls, episode: Episode) -> None:
        ep_num = str(episode.number).replace(".0", "").replace(".", "_")
        await cls.update(Set({f"episodes.{ep_num}" : episode}))

    @classmethod
    async def check_time(cls, title: Title) -> timedelta:
        release = await cls.find_one(cls.id == title.id)
        try:
            ep = list(release.episodes)[-1]
            ep = release.episodes.get(ep)
        except Exception as ex:
            log.error(ex)
            log.error("Не нашли эпизода в БД")
            return False

        td = datetime.fromtimestamp(title.updated) - ep.date
        return td
    
    @classmethod
    async def set_deadline(cls, chat_id: int, days: int) -> None:
        release = await cls.get_by_chat_id(chat_id)
        release.days_to_work = days

        await release.save()

    @classmethod
    async def set_en_title(cls, chat_id: int, title: str) -> None:
        try:
            release = await cls.get_by_chat_id(chat_id)
            release.en_title = title
            await release.save()
        except Exception as ex:
            log.error("DB problem!")
            log.error(ex)

    @classmethod
    async def finish_release(cls, id: int) -> None:
        try:
            release = await cls.find_one(cls.id == id)
            release.is_ongoing = False
            await release.save()

        except Exception as ex:
            log.error("DB problem!")
            log.error(ex)