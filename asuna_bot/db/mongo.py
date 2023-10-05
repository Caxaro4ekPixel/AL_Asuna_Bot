from typing import List

from beanie import WriteRules
from .odm import (
    User, Chat, Release, 
    Episode, BotConfig, NyaaRssConf, 
    AlApiConf
)
from beanie.operators import Set
from loguru import logger as log

class Mongo:

    @staticmethod
    async def get_all_user_ids() -> List:
        all_users = await User.find_all().to_list()
        return [user.id for user in all_users]

    @staticmethod
    async def get_chat(chat_id: int) -> Chat:
        chat = await Chat.get(chat_id)
        return chat

    @staticmethod
    async def get_chat_id_by_release_id(release_id: int) -> Chat:
        release = await Release.find_one(Release.id == release_id)
        if release:
            chat = await Chat.find_one(Chat.id == release.chat_id)
            return chat
        return None

    @staticmethod
    async def get_all_ongoing_chats() -> List:
        try:
            return await Chat.find(Chat.release.is_ongoing == True,  # noqa: E712
                                   fetch_links=True).to_list()
        except Exception as ex:
            log.error("DB problem!")
            log.error(ex)

    @staticmethod
    async def get_release(release_id: int) -> Release:
        return await Release.find_one(Release.id == release_id)

    @staticmethod
    async def get_release_by_chat_id(chat_id: int) -> Release:
        return await Release.find_one(Release.chat_id == chat_id)

    @staticmethod
    async def get_nyaa_rss_conf() -> NyaaRssConf:
        conf = await BotConfig.find({}).first_or_none()
        return conf.nyaa_rss

    @staticmethod
    async def get_al_conf() -> AlApiConf:
        conf = await BotConfig.find({}).first_or_none()
        return conf.al_api


    @staticmethod
    async def get_bot_conf() -> BotConfig:
        return await BotConfig.find({}).first_or_none()

    @staticmethod
    async def add_chat(chat_id: int, name: str) -> None:
        new_chat = Chat(id=chat_id, name=name, release=None)
        await new_chat.create()

    @staticmethod
    async def add_release(chat_id: int, release: Release) -> None:
        if not Release.find_one(Release.id == release.id):
            await release.insert()

        chat = await Chat.find_one(Chat.id == chat_id)
        chat.release = release
        await chat.save(link_rule=WriteRules.WRITE)

    @staticmethod
    async def add_episode(release: Release, episode: Episode) -> None:
        ep_num = str(episode.number).replace(".0", "").replace(".", "_")
        await release.update(Set({f"episodes.{ep_num}" : episode}))


    @staticmethod
    async def add_user(id: int, name: str, role: list[str]) -> None:
        new_user = User(id=id, name=name, role=role)
        await new_user.create()

    @staticmethod
    async def update_chat_conf(chat_id: int, **kwargs) -> None:
        for key, val in kwargs.items():
            await Chat.find_one(Chat.id == chat_id).update(
                Set({f"config.{key}": val})
            )

    @staticmethod
    async def update_nyaa_rss_conf(**kwargs) -> None:
        for key, val in kwargs.items():
            await BotConfig.find({}).update(
                Set({f"nyaa_rss.{key}": val})
            )

    @staticmethod
    async def update_al_api_conf(**kwargs) -> None:
        for key, val in kwargs.items():
            await BotConfig.find({}).update(
                Set({f"al_api.{key}": val})
            )