"""
Бот может конвертировать субтитры формата .ass в .srt 
удаляя лишнее и выделяя надписи
"""
from aiogram import Router, Bot
from aiogram.types import Message 
from aiogram.filters import Command
from asuna_bot.config import CONFIG
from asuna_bot.filters.admins import AllowedUserFilter
from asuna_bot.utils.subs import convert_to_srt

convert_router = Router()
convert_router.message.filter(AllowedUserFilter(), Command("srt"))
bot = Bot(token=CONFIG.bot.token)

@convert_router.message()
async def ass_to_srt(msg: Message):
    try:
        msg.reply_to_message.document.file_id
    except Exception:
        msg.answer("Команда работает реплаем на сообщение с сабом")
        return

    file_info = await bot.get_file(msg.reply_to_message.document.file_id)
    ass_file = await bot.download_file(file_info.file_path)
    srt_file = convert_to_srt(ass_file.read(), msg.reply_to_message.document.file_name)
    
    await msg.answer_document(srt_file)
    