import asyncio
from aiohttp import ClientSession

from loguru import logger as log

from asuna_bot.main.chat_controller import ChatController
from asuna_bot.db.odm import Chat, NyaaRssConf, BotConfig
from asuna_bot.api.models import NyaaTorrent
from .rss_parser import rss_to_json

from anilibria import AniLibriaClient


class ApiRssObserver:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self.chats = dict()
        self._session = ClientSession()
        self._running: bool = True
        self._config: NyaaRssConf
        self._al_client = AniLibriaClient(logging=True)

    async def _register_chats(self):
        all_ongoings = await Chat.get_all_ongoing_chats()
        self.chats.clear()
        for chat in all_ongoings:
            chat: Chat
            self.chats[chat.id] = ChatController(chat)

    async def _push_rss_update(self, torrents) -> None:
        for chat in self.chats.values():
            chat: ChatController
            await chat.nyaa_update(torrents)

    async def _push_title_update(self, titles: list) -> None:
        for chat in self.chats.values():
            chat: ChatController
            log.debug("_push_title_update")
            await chat.release_up(titles)

    # async def _push_notify(self) -> None:
    #     for chat in self.chats.values():
    #         chat: ChatController
    #         log.debug("_push_notify")
    #         await chat.notify()

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

    async def _http_request(self, url: str, params: dict) -> list:
        try:
            response = await self._session.get(url, params=params, timeout=30)
            json = await response.json()
        except Exception as ex:
            log.error(ex)
            return None

        return json

    async def start_polling(self):
        """Поллинг rss ленты"""
        log.info("Start Nyaa.si RSS AND AniLibria updates polling")
        while self._running:
            self._config = await BotConfig.get_nyaa_rss_conf()
            conf = self._config
            self._build_params_str()

            log.debug("Формируем список онгоингов...")
            await self._register_chats()
            log.debug(self.chats.keys())
            parsed_rss = await self._rss_request(conf.base_url, conf.params, conf.limit)

            if parsed_rss is None:
                await asyncio.sleep(conf.interval)
                continue

            rss_last_id = parsed_rss[0].get("id")

            if rss_last_id <= conf.last_id:
                log.info("Нет новых торрентов на няшке")
            else:
                torrents = [
                    NyaaTorrent(**torrent)
                    for torrent in parsed_rss
                    if torrent.get("id") > conf.last_id
                ]
                await self._push_rss_update(torrents)  # Делаем пуш чатам
                await BotConfig.update_nyaa_rss_conf(last_id=rss_last_id)

            al_conf = await BotConfig.get_al_conf()
            log.debug(f"al_conf={al_conf.model_dump_json()}")
            url = "http://api.anilibria.tv/v2/getUpdates"
            params = {
                "since": al_conf.last_update,
                "limit": 40,
                "filter": "id,updated,player.series.last",
            }
            titles = await self._http_request(url, params)
            log.debug(f"titles={titles}")
            if titles:
                lst_site_upd = titles[0]["updated"]
                if lst_site_upd > al_conf.last_update:
                    await BotConfig.update_al_api_conf(last_update=lst_site_upd + 1)
                    log.debug(f"last_site_update={lst_site_upd}")
                    await self._push_title_update(titles)
                else:
                    log.info("Нет новых апдейтов на сайте")

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
