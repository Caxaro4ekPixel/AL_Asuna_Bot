from beanie import Document, Link, WriteRules
from typing import List, Optional
from pydantic import BaseModel
from .release import Release
from loguru import logger as log
from beanie.operators import Set


class ChatConfig(BaseModel):
    submitter: str = "[Erai-raws]"
    show_alerts: bool = True
    show_fhd: bool = True
    show_hd: bool = True
    show_sd: bool = True
    show_direct_links: bool = True
    show_magnet_links: bool = True
    send_torrent_files: bool = True
    e2e_numbering: bool = False


class Chat(Document):
    id: int
    status: str = ""
    msg_id: int = 0
    name: str
    config: ChatConfig = ChatConfig()
    release: Optional[Link[Release]] = None

    class Settings:
        name = "chats"

    @classmethod
    async def get_by_id(cls, chat_id: int) -> Optional["Chat"]:
        return await cls.find_one(cls.id == chat_id)

    @classmethod
    async def get_all_ongoing_chats(cls) -> Optional[List["Chat"]]:
        try:
            return await cls.find(
                cls.release.is_ongoing == True,  # noqa: E712
                fetch_links=True,
            ).to_list()
        except Exception as ex:
            log.error("chat.py -> get_all_ongoing_chats")
            log.error(ex)

    @classmethod
    async def change_settings(cls, chat_id: int, key: str, val: bool | str) -> None:
        chat = await cls.find_one(cls.id == chat_id)
        await chat.set({f"config.{key}": val})

    @classmethod
    async def update_chat_conf(cls, chat_id: int, **kwargs) -> None:
        for key, val in kwargs.items():
            await cls.find_one(Chat.id == chat_id).update(Set({f"config.{key}": val}))

    @classmethod
    async def add(chat_id: int, name: str) -> None:
        new_chat = Chat(id=chat_id, name=name, release=None)
        await new_chat.create()

    @classmethod
    async def add_release(cls, chat_id: int, release: Release) -> None:
        if not Release.find_one(Release.id == release.id):
            await release.insert()

        chat = await cls.find_one(cls.id == chat_id)
        chat.release = release
        await chat.save(link_rule=WriteRules.WRITE)