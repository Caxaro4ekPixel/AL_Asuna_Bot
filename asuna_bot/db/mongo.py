
from typing import List
from .odm import User, Chat, Release, Episode, BotConfig, NyaaRssConf
from beanie.operators import Set


class Mongo:
    
    @staticmethod
    async def get_all_user_ids() -> List:
        return await User.find_all().to_list()


    @staticmethod
    async def get_chat(chat_id: int):
        chat = await Chat.get(chat_id)
        return chat


    @staticmethod
    async def get_all_ongoing_chats() -> List:
        return await Chat.find(Chat.release.is_ongoing == True,   # noqa: E712
                               fetch_links=True).to_list()


    @staticmethod
    async def get_release(release_id: int) -> Release:
        return await Release.find_one(Release.id == release_id)


    @staticmethod
    async def get_nyaa_rss_conf() -> NyaaRssConf:
        conf = await BotConfig.find({}).first_or_none()
        return conf.nyaa_rss
    

    @staticmethod
    async def get_bot_conf() -> BotConfig:
        return await BotConfig.find({}).first_or_none()


    @staticmethod
    async def add_chat(chat_id: int, name: str) -> None:
        new_chat = Chat(id=chat_id, name=name, release=None)
        await new_chat.create()


    @staticmethod
    async def add_release(chat_id: int, release: Release) -> None:
        await release.create()
        await Chat.find_one(Chat.id == chat_id).update(
            Set({Chat.release: release})
        )


    @staticmethod
    async def add_episode(release: Release, episode: Episode) -> None:
        ep_num = str(episode.number)
        await release.update(Set({"episodes" : {ep_num : episode}}))

    
    @staticmethod
    async def add_user(id: int, full_name: str, 
                       user_name: str, role: list[str]) -> None:
        new_user = User(id=id, full_name=full_name, 
                        user_name=user_name, role=role)
        await new_user.create()


    @staticmethod
    async def update_chat_conf(chat_id: int, **settings) -> None:
        for key, val in settings.items():
            await Chat.find_one(Chat.id == chat_id).update(
                Set({f"chats.config.{key}" : val})
            )


    @staticmethod
    async def update_nyaa_rss_conf(**settings) -> None:
        for key, val in settings.items():
            await BotConfig.find({}).update(
                Set({f"nyaa_rss.{key}" : val})
            )