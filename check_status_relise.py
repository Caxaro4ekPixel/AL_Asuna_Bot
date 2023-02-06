from dateutil.parser import parse
import calendar
import io
import xmltodict
from utils import log, normolize_text, similarity
import requests
from telebot import types
from telegram import ParseMode
from datetime import datetime
import time


def check_status_relise_in_chats(bot, con):
    cur = con.cursor()
    try:
        log("start check status relise in chats", "info")
        cur.execute('''SELECT * FROM results r WHERE time = -1;''')
        res = cur.fetchall()
        for i in res:
            bottons = [
                [types.InlineKeyboardButton(text="Перевод/редактура", callback_data=f'translation.{i[1]}')],
                [types.InlineKeyboardButton(text="Озвучка", callback_data=f'voiceover.{i[1]}')],
                [types.InlineKeyboardButton(text="Тайминг/фиксы", callback_data=f'timing.{i[1]}')],
                [types.InlineKeyboardButton(text="Сборка", callback_data=f'assembling.{i[1]}')]
            ]
            bot.send_message(i[1], f'Каков статус релиза?', reply_markup=types.InlineKeyboardMarkup(bottons))
    except Exception as err:
        log(f"ERROR {err}", "error")
