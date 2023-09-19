"""
командой /start пытается найти релиз по названию чата 
если неудачо: 
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

from anilibria import AniLibriaClient, Title


start_router = Router()
start_router.message.filter(AllowedUserFilter(), Command("start"))


async def add_release(message: types.Message, title: Title):
    release = Release(
                id=title.id,
                chat_id=message.chat.id,
                status=title.status.string,
                code=title.code,
                en_title=title.names.en,
                ru_title=title.names.ru,
                is_ongoing=True,
            )
    await db.add_release(message.chat.id, release)


async def is_title_exist(message, title_id):
# если тайтл с этим id уже существует где-то в базе
    chat = await db.get_chat(title_id)
    log.info(chat)
    if chat: 
        if chat._id != message.chat.id:
            await message.answer(
                "Этот тайтл уже закреплен за другим чатом!\n" 
                + html.bold(chat.name)
            )

        if chat._id == message.chat.id:
            await message.answer("Этот тайтл уже закреплен за текущим чатом!")
        
        return True
    return False


async def auto_search_title(message: types.Message):
    libria = AniLibriaClient()
    try:
        titles = await libria.search_titles(
            message.chat.title.split("/")[0], 
            filter="id,code,names,status,season,type,team"
        )
    except Exception as e:
        log.error(e)

    del libria
    await message.answer(titles[0].code)
    
    if titles.count > 1:
        await message.answer("Найдено несколько тайтлов!")
    else:
        await add_release(message, titles[0])
        await message.answer(f"Тайтл: {html.bold(titles[0].names.ru)} закреплен за этим чатом")


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
        await auto_search_title(message)

    else:
        await id_search_title(message, command)


@start_router.message(ChatTypeFilter(chat_type="group"))
async def cmd_start_group(message: types.Message):
    await message.answer(
            f"Для моей работы, выдайте права с пунктом {html.bold('Анонимность')}"
        )