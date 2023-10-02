from beanie import Document, Link
from typing import Optional
from pydantic import BaseModel
from .release import Release

class ChatConfig(BaseModel):
    submitter          : str  = "[Erai-raws]"
    show_alerts        : bool = True
    show_fhd           : bool = True
    show_hd            : bool = True
    show_sd            : bool = True
    show_direct_links  : bool = True
    show_magnet_links  : bool = True
    send_torrent_files : bool = True
    e2e_numbering      : bool = False


class Chat(Document):
    id      : int
    status  : str = ""
    msg_id  : int = 0
    name    : str
    config  : ChatConfig = ChatConfig()
    release : Optional[Link[Release]] = None
    
    class Settings:
        name = "chats"

    @classmethod
    async def get_by_id(cls, chat_id: int) -> Optional["Chat"]:
        return await cls.find_one(cls.id == chat_id)

    @classmethod
    async def change_settings(cls, chat_id: int, key: str, val: bool | str) -> None:
        chat = await cls.find_one(cls.id == chat_id)
        await chat.set({f"config.{key}": val})