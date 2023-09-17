import asyncio
import json
import random
from typing import List
from aiohttp import ClientSession
from loguru import logger as log
from asuna_bot.api.nya.model import NyaaTorrent
from asuna_bot.db.mongo import Mongo as db
from aiogram import Bot, html
from difflib import SequenceMatcher
from asuna_bot.config import CONFIG
from asuna_bot.db.odm import Chat, Release, Episode
from datetime import timedelta
from aiogram.types import BufferedInputFile, Message
from pytz import timezone


SITE_URL = "https://www.anilibria.tv/release/"
BACK_URL = "https://backoffice.anilibria.top/resources/anime__releases/"

class ChatControl:
    def __init__(self, chat: Chat) -> None:
        self._chat = chat
        self._release: Release = self._chat.release
        self._torrents: List[NyaaTorrent] = []
        self._ep: Episode
        self._bot: Bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')
        self._last_msg: Message
        self._admin_chat = CONFIG.bot.admin_chat

    async def nyaa_update(self, torrents: List[NyaaTorrent]) -> None:
        for torrent in torrents:
            s1 = self._release.en_title
            s2 = torrent.title

            if self._chat.config.submitter in torrent.submitter:
                ratio = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
                log.debug(f"comparing: {s1} <<AND>> {s2}; ratio={ratio}")
                
                if ratio > 0.75:
                   self._torrents.append(torrent)
                   
        if self._torrents:
            await self._add_new_episode() 
            await self._send_message_to_chat()
            # await self.send_torrents_to_chat()
            # await self._bot.pin_chat_message(self._admin_chat, self._last_msg.message_id)
            # await self.del_last_srvc_msg()
            self._torrents = []


    async def _add_new_episode(self):
        torrent = self._torrents[0]
        if self._release.episodes:
            ep = list(self._release.episodes)[-1]
            if float(ep) == torrent.serie:
                # update_episode
                log.info("Эпизод уже существует")
                return


        if self._release.is_commer:
            deadline = torrent.date + timedelta(hours=24)
        elif self._release.is_top:
            deadline = torrent.date + timedelta(hours=48)
        else:
            days = self._release.days_to_work
            deadline = torrent.date + timedelta(hours=24*days)


        self._ep = Episode(
            number=torrent.serie,
            date=torrent.date,
            deadline_at=deadline,
            status="Just released",
            torrents=self._torrents
        )
        await db.add_episode(self._release, self._ep)
        log.info("Добавили новый эпизод")
         

    def _dispatch_torrents(self) -> NyaaTorrent:
        fhd, hd, sd = None, None, None

        for torrent in self._torrents:
            match torrent.quality:
                case "1080p":
                    fhd = torrent
                case "720p":
                    hd = torrent
                case "480p":
                    sd = torrent

        return fhd, hd, sd


    def _random_kaomoji(self) -> str:
        with open('emoticon_dict.json', 'r', encoding='utf-8') as f:
            emoticon_dict = json.load(f)
            kaomoji = list(emoticon_dict.keys())
        
        rnd = random.randint(0, len(kaomoji)-1)
        return kaomoji[rnd]


    def _craft_message_text(self) -> str:
        fhd, hd, sd = self._dispatch_torrents()
        rel = self._release
        conf = self._chat.config
        torr = self._torrents[-1]
        ep = self._ep
        
        
        msk = timezone("Europe/Moscow")
        fmt = "%d.%m  %H:%M"
        deadline = ep.deadline_at.astimezone(msk).strftime(fmt)
        
        
        text1 = [
            f"{html.bold(rel.ru_title)}",
            html.italic("Серия — " + str(ep.number).removesuffix(".0")),
            "",
            html.italic(torr.submitter),
        ]
        

        text2 = []
        if conf.show_fhd and fhd:
            a = f"『 {html.link(fhd.size, fhd.file_url)}"
            b = f" | {html.link('🧲', fhd.magnet)} 』"
            text2 += ["{}{}".format(a,b)]
        if conf.show_hd and hd:
            a = f"『 {html.link(hd.size, hd.file_url)}"
            b = f" | {html.link('🧲', hd.magnet)} 』"
            text2 += ["{}{}".format(a,b)]
        if conf.show_sd and sd:
            a = f"『 {html.link(sd.size, sd.file_url)}"
            b = f" | {html.link('🧲', sd.magnet)} 』"
            text2 += ["{}{}".format(a,b)]


        text3 = [
            "",
            f"﴾{html.link('❤️Сайт❤️', SITE_URL+rel.code+'.html')}  ‖  {html.link('🖤Админка🖤', BACK_URL+str(rel.id))}﴿", # noqa: E501 
            "",
            f"⏳<i>Дедлайн</i>:  <b>{deadline} МСК</b>",
            html.spoiler(self._random_kaomoji())
        ]

        
        text4 = [
            "",
            html.link("nyaa link (только для теста)", self._torrents[-1].url),
            f"chat_id: {html.code(rel.chat_id)}"
        ]
        return "\n".join(text1+text2+text3+text4)


    async def _send_message_to_chat(self):
        text = self._craft_message_text()
        self._last_msg = await self._bot.send_message(self._admin_chat, text, 
                                     disable_web_page_preview=True)
        await asyncio.sleep(1)
    

    async def _send_torrents_to_chat(self):
        session = ClientSession()
        for torrent in self._torrents:
            response = await session.get(torrent.file_url, allow_redirects=True)
            
            title = '{:.20}'.format(self._release.ru_title) + "..." \
            if len(self._release.ru_title) >= 20 else self._release.ru_title

            filename = f"[{torrent.quality}] {title} [{str(torrent.serie)}].torrent"
            bytes = await response.read()
            file = BufferedInputFile(bytes, filename)
            await self._bot.send_document(self._admin_chat, file)
            await asyncio.sleep(1)
        await session.close()


    async def _del_last_srvc_msg(self):
        if self._last_msg:
            await self._bot.delete_message(self._admin_chat, self._last_msg.message_id+1)