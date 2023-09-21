"""
Командой /start пытается найти релиз по названию чата
если неудачно:
просит ввести id релиза
отправляет клавиатуру с первичными настройками релиза для этого чата
срабатывает только в чатах, которых еще нет в БД  
"""

from aiogram import Router, types, html
from aiogram.filters import CommandObject, Command
from loguru import logger as log
from asuna_bot.db.mongo import Mongo as db
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.filters.chat_type import ChatTypeFilter
from asuna_bot.db.odm import Release
from aiogram import Bot
from anilibria import AniLibriaClient, Title
from asuna_bot.config import CONFIG

start_router = Router()
start_router.message.filter(AllowedUserFilter(), Command("start"))


async def add_release(chat_id, title: Title):
    release = Release(
        id=title.id,
        chat_id=chat_id,
        status=title.status.string,
        code=title.code,
        en_title=title.names.en,
        ru_title=title.names.ru,
        is_ongoing=True,
        episodes=None,
    )
    await db.add_release(chat_id, release)


async def is_title_exist(message, title_id):
    # если тайтл с этим id уже существует где-то в базе
    chat = await db.get_chat_id_by_title_id(title_id)
    if chat:
        if chat.id != message.chat.id:
            await message.answer(
                "Этот тайтл уже закреплен за другим чатом!\n"
                + html.bold(chat.name)
            )

        if chat.id == message.chat.id:
            await message.answer("Этот тайтл уже закреплен за текущим чатом!")

        return True
    return False


async def search_title(message: types.Message):
    libria = AniLibriaClient()
    try:
        titles = await libria.search_titles(
            message.chat.title.split("/")[0],
            filter="id,code,names,status,season,type,team"
        )
    except Exception as e:
        log.error(e)
        return

    del libria
    return titles


async def send_title_to_chat(titles, chat_id):
    bot = Bot(token=CONFIG.bot.token)

    await bot.send_message(chat_id, titles.list[0].code)

    if titles.pagination.total_items > 1:
        await bot.send_message(chat_id, "Найдено несколько тайтлов!")
        # TODO добавить кнопки с тайтлами
    else:
        await add_release(chat_id, titles.list[0])
        await bot.send_message(chat_id, f"Тайтл: {html.bold(titles.list[0].names.ru)} закреплен за этим чатом")


async def id_search_title(message: types.Message, command: CommandObject):
    al_title_id = int(command.args)

    exist = await is_title_exist(message, al_title_id)
    if exist:
        return

    libria = AniLibriaClient()
    try:
        title = await libria.get_title(al_title_id, filter="id,code,names,status,season,type,team")
        if not title:
            await message.answer(f"Тайтл c id {str(al_title_id)} не найден 🧐")
            return False

        await add_release(message, title)
        await message.answer(f"Тайтл: {html.bold(title.names.ru)} закреплен за этим чатом")

    except AttributeError as err:
        log.error(err)
        await message.answer(str(err))


@start_router.message(ChatTypeFilter(chat_type="supergroup"))
async def cmd_start(message: types.Message, command: CommandObject):
    # если первый раз запускаем команду
    chat = await db.get_chat(message.chat.id)
    if not chat:
        await db.add_chat(message.chat.id, message.chat.title)

    if command.args is None or not command.args.isdigit():
        titles = await search_title(message)
        await send_title_to_chat(titles, message.chat.id)
    else:
        await id_search_title(message, command)


@start_router.message(ChatTypeFilter(chat_type="group"))
async def cmd_start_group(message: types.Message):
    await message.answer(
        f"Для моей работы, выдайте права с пунктом {html.bold('Анонимность')}"
    )
