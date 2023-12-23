import asyncio
from typing import List
from aiohttp import ClientSession
from loguru import logger as log
from asuna_bot.api.models import NyaaTorrent
from asuna_bot.db.mongo import Mongo as db
from aiogram import Bot, html
from difflib import SequenceMatcher
from asuna_bot.config import CONFIG
from asuna_bot.db.odm import Chat, Release, Episode
from datetime import timedelta, datetime
from aiogram.types import BufferedInputFile, Message
from aiogram.exceptions import TelegramBadRequest
from asuna_bot.utils import craft_time_str, random_kaomoji

import pytz
utc = pytz.UTC


#####################TODO Брать это из БД  ####################
SITE_URL = "https://www.anilibria.tv/release/"
BACK_URL = "https://backoffice.anilibria.top/resources/anime__releases/"
msk = pytz.timezone("Europe/Moscow")
fmt = "%d.%m  %H:%M"
fmt2 = "%d дней %H Часов %M Минут"
###############################################################

class ChatController:
    def __init__(self, chat: Chat) -> None:
        self._chat = chat
        self._release: Release = self._chat.release
        self._torrents: List[NyaaTorrent] = []
        self._ep: Episode
        self._bot: Bot = Bot(token=CONFIG.bot.token, parse_mode='HTML')
        self._last_msg: Message

        self.chat_id = self._chat.id # Для прода
        # self.chat_id = CONFIG.bot.admin_chat # Для теста

    async def nyaa_update(self, torrents: List[NyaaTorrent]) -> None:
        for torrent in torrents:
            s1 = self._release.en_title.lower()
            s2 = torrent.title.lower()
            
            sub = self._chat.config.submitter
            if sub.startswith("["):
                pass
            else:
                sub = "["+ sub + "]"

            if sub in torrent.submitter:
                ratio = SequenceMatcher(None, s1, s2).ratio()
                log.debug(f"{s1} <<<AND>>> {s2} with ratio={ratio}")
                if ratio > 0.70:
                    self._torrents.append(torrent)

        if self._torrents:
            await self._add_new_episode()
            await self._send_message_to_chat()
            await self._send_torrents_to_chat()
            try:
                await self._bot.pin_chat_message(self._chat.id, self._last_msg.message_id)
            except TelegramBadRequest:
                log.debug("Не удалось закрепить сообщение!")
                pass
            self._torrents.clear()

    async def release_up(self, titles: list) -> None:
        for title in titles:
            log.debug(title)
            if int(title["id"]) == self._release.id:
                log.debug("Есть совпадение")
                try:
                    log.debug("Попытка найти эпизод в Бд")
                    ep = list(self._release.episodes)[-1]
                    self._ep = self._release.episodes.get(ep)
                except Exception as ex:
                    log.error(ex)
                    log.error("Не нашли эпизода в БД")
                    return

                log.debug("Нашли EP:")
                log.debug(self._ep.model_dump_json())
                uploaded_at = datetime.utcfromtimestamp(float(title["updated"]))
                td = uploaded_at - self._ep.date

                log.debug(f"uploaded_at={uploaded_at}")
                log.debug(f"timedelta={td}")
                
                time_str = craft_time_str(td)
                log.debug(f"Вышла за: {time_str}")
                
                self._ep.overall_time = int(td.total_seconds())
                self._ep.uploaded_at = uploaded_at
                self._ep.status = f"Вышла за {time_str}"
                
                await self._release.save()

                log.debug("Обновили overall_time и uploaded_at в БД")
                last_ep = title["player"]["series"]["last"]
                log.debug(f"last_ep={last_ep}")
                log.debug(f"Отправляем сообщение в чат {self.chat_id}")

                await self._bot.send_message(
                    self.chat_id,
                    f"{last_ep}-я серия вышла за:\n{time_str}"
                )
    

    # async def notify(self) -> None:
    #     ep = list(self._release.episodes)[-1]
    #     ep = self._release.episodes.get(ep)
            
    async def _add_new_episode(self):
        torrent = self._torrents[0]
        if self._release.episodes:
            ep = list(self._release.episodes)[-1]
            self._ep = self._release.episodes.get(ep)

            if float(ep) == torrent.serie:
                #TODO обновить сообщение с инфой, добавить ссылки на новый качества  
                # await self._send_torrents_to_chat()
                return

        if self._release.is_commer:
            deadline = torrent.date + timedelta(hours=24)
        elif self._release.is_top:
            deadline = torrent.date + timedelta(hours=48)
        else:
            days = self._release.days_to_work
            deadline = torrent.date + timedelta(hours=24 * days)

        self._ep = Episode(
            number=torrent.serie,
            date=torrent.date,
            deadline_at=deadline,
            status="В работе",
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

    def _craft_message_text(self) -> str:
        fhd, hd, sd = self._dispatch_torrents()
        rel = self._release
        conf = self._chat.config
        torr = self._torrents[-1]
        ep = self._ep
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
            text2 += ["{}{}".format(a, b)]
        if conf.show_hd and hd:
            a = f"『 {html.link(hd.size, hd.file_url)}"
            b = f" | {html.link('🧲', hd.magnet)} 』"
            text2 += ["{}{}".format(a, b)]
        if conf.show_sd and sd:
            a = f"『 {html.link(sd.size, sd.file_url)}"
            b = f" | {html.link('🧲', sd.magnet)} 』"
            text2 += ["{}{}".format(a, b)]

        text3 = [
            "",
            f"﴾{html.link('❤️Сайт❤️', SITE_URL + rel.code + '.html')}  ‖  {html.link('🖤Админка🖤', BACK_URL + str(rel.id))}﴿",
            "",
            f"⏳<i>Дедлайн</i>:  <b>{deadline} МСК</b>",
            html.spoiler(random_kaomoji())
        ]

        return "\n".join(text1 + text2 + text3)

    async def _send_message_to_chat(self):
        text = self._craft_message_text()
        self._last_msg = await self._bot.send_message(self.chat_id, text,
                                                      disable_web_page_preview=True)
        await asyncio.sleep(1)

    async def _send_torrents_to_chat(self):
        session = ClientSession()
        for torrent in self._torrents:
            response = await session.get(str(torrent.file_url), allow_redirects=True)

            title = '{:.20}'.format(self._release.ru_title) + "..." \
                if len(self._release.ru_title) >= 20 else self._release.ru_title

            serie = str(torrent.serie).removesuffix(".0")

            filename = f"[{torrent.quality}] {title} [{serie}].torrent"
            bytes = await response.read()
            file = BufferedInputFile(bytes, filename)
            await self._bot.send_document(self.chat_id, file)
            await asyncio.sleep(2)
        await session.close()
