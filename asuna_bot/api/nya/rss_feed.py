import asyncio
from aiohttp import ClientSession

from loguru import logger as log

from asuna_bot.db.mongo import Mongo as db
from asuna_bot.db.odm.bot_conf import NyaaRssConf
from asuna_bot.main.chat_control import ChatControl

from .model import NyaaTorrent
from .rss_parser import rss_to_json


class NyaaRssFeed:
    def __init__(self) -> None:
        self._chats = dict()
        self._session = ClientSession()
        self._running : bool = True
        self._config : NyaaRssConf

    async def _register_chats(self):
        all_ongoings = await db.get_all_ongoing_chats()
        for chat in all_ongoings:
            if chat.id not in self._chats.keys():
                await self._register_chat(chat)
                
        
    async def _register_chat(self, chat):
        new_chat = ChatControl(chat)
        self._chats[chat.id] = new_chat


    async def _push_update(self, torrents) -> None:
        for chat in self._chats.values():
            await chat.nyaa_update(torrents)
            

    async def _rss_request(self, url: str, params: dict, limit):
        try:
            response = await self._session.get(url, params=params, timeout=30)
            raw = await response.text()
        except Exception as ex:
            log.error(ex)
            return None

        try:
            json = rss_to_json(raw, limit=limit)
        except Exception as ex:
            json = None
            log.debug(ex)
        
        return json


    async def start_polling(self):
        """Поллинг rss ленты"""
        log.info("Start Nyaa.si RSS polling")
        while self._running:
            self._config = await db.get_nyaa_rss_conf()
            self._build_params_str()

            conf = self._config
            await self._register_chats()

            parsed_rss = await self._rss_request(conf.base_url, conf.params, conf.limit)
            
            if parsed_rss is None:
                await asyncio.sleep(conf.interval)
                continue
            
            rss_last_id = parsed_rss[0].get("id")

            if rss_last_id <= conf.last_id:
                log.info("Нет новых торрентов")
            else:
                torrents = [
                    NyaaTorrent(**torrent) 
                    for torrent in parsed_rss 
                    if torrent.get("id") > conf.last_id
                ]
                await self._push_update(torrents) # Делаем пуш чатам
                await db.update_nyaa_rss_conf(last_id=rss_last_id)

            await asyncio.sleep(conf.interval)


    def _build_params_str(self) -> None:
        if self._config.submitters:
            if len(self._config.submitters) > 1:
                s = " || ".join(self._config.submitters)
            else: 
                s = self._config.submitters[-1]
            self._config.params["q"] += s

        if self._config.exceptions:
            if len(self._config.exceptions) > 1:
                e = " -".join(self._config.exceptions)
            else:
                e = f" -{self._config.exceptions[-1]}"
            self._config.params["q"] += e