import time
import telebot
from telebot import types
import sqlite3
import requests
import threading
from telegram import ParseMode
from datetime import datetime, timedelta
import os
from utils import name_month, name_week_day, log, convert_to_preferred_format
from check_time import checkTime
from reader_RSS import check
from decouple import config

bot = telebot.TeleBot(config("TOKEN"), parse_mode=None)
con = sqlite3.connect('db.db', check_same_thread=False)


@bot.message_handler(commands=['start'])
def start(message):
    log(f"send start {message.chat.id, message.chat.username, message.text}")
    bot.send_message(chat_id=734264203,
                     text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    # if message.chat.id == 734264203:
    #     a = bot.send_message(734264203, "asdasdadsasdads")
    #     bot.pin_chat_message(chat_id=message.chat.id, message_id=a.message_id)
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        relese_id = message.text.replace("/start ", "")
        response = requests.get(f'https://api.anilibria.tv/v2/getTitle?id={relese_id}').json()
        if "error" in response:
            bot.send_message(message.chat.id, '🧐Такого релиза не существует!🧐')
        else:
            bottons = [[types.InlineKeyboardButton(text="Да", callback_data='1')],
                       [types.InlineKeyboardButton(text="Нет", callback_data='0')]]
            bot.send_message(message.chat.id, f'Релиз: {response["names"]["ru"]}?\nID: {relese_id}',
                             reply_markup=types.InlineKeyboardMarkup(bottons))
    else:
        pass


@bot.message_handler(commands=['update'])
def update(message):
    log(f"select update {message.chat.id, message.chat.username, message.text}")
    bot.send_message(chat_id=734264203,
                     text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        cur = con.cursor()
        relese_id = message.text.replace("/update ", "")
        cur.execute(f'''select * from chats where id={message.chat.id}''')
        chat = cur.fetchone()

        response = requests.get(f'https://api.anilibria.tv/v2/getTitle?id={relese_id}').json()
        if "error" in response:
            bot.send_message(message.chat.id, '🧐Такого релиза не существует!🧐')
        elif chat:
            cur.execute(f'''update chats set id_relese={relese_id} where id={message.chat.id}''')
            bot.send_message(chat_id=message.chat.id, text="✅Перезапись успешно прошла!✅")

        con.commit()
        cur.close()
    else:
        bot.send_message(message.chat.id, 'Не ТроЖ бота в лс)')


@bot.message_handler(commands=['stop'])
def stop(message):
    log(f'send stop {message.chat.id, message.chat.username, message.text}')
    bot.send_message(734264203, "АЛЯЯЯРМ!")
    if message.chat.id in [253296124, 734264203, 1625017611, 470092294]:
        bot.send_message(message.chat.id, "Bot is deactivated")
        bot.stop_bot()


@bot.message_handler(commands=['raw'])
def set_raw(message):
    log(f'set raw {message}', 'info')
    bot.send_message(chat_id=734264203,
                     text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        try:
            raw = message.text.replace("/raw ", "")
            if '/raw' in raw:
                bot.send_message(message.chat.id, "❌Некоректно введено название❌")
            else:
                cur = con.cursor()
                cur.execute(f'''update chats set raw='{raw}' where id = {message.chat.id};''')
                con.commit()
                cur.close()
                bot.send_message(message.chat.id, f'✅Успешно изменено на "{raw}"✅')
        except:
            log(f'error set raw {message}', 'error')
    else:
        bot.send_message(message.chat.id, 'Не ТроЖ бота в лс)')


@bot.message_handler(commands=['report'])
def result(message):
    log(f'get report {message.chat.id}, {message.chat.username}, {message.chat.type}', 'info')
    bot.send_message(chat_id=734264203,
                     text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    bot.send_message(message.chat.id, "📈Ожидайте! формирую отчёт📈")
    cur = con.cursor()
    try:
        response = requests.get(f"https://api.anilibria.tv/v2/getSchedule").json()
        mess_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for week in response:
            for relese in week['list']:
                cur.execute(f'''select * from results where id={relese["id"]}''')
                res = cur.fetchone()
                a = datetime.fromtimestamp(relese['updated'])
                time_up = f"{a.day} {name_month(a.month)} {a.hour if a.hour > 9 else f'0{a.hour}'}:{a.minute if a.minute > 9 else f'0{a.minute}'}:{a.second if a.second > 9 else f'0{a.second}'}"

                em = "🔘"
                if res:
                    if res[3] == -1:
                        time_up = f"В работе! (предыдущая серия вышла {time_up})"
                        em = "🎤"
                    else:
                        timer = timedelta(seconds=int(res[3]))
                        days = timer.days
                        _time = convert_to_preferred_format(timer.seconds)
                        daysstr = ('день' if 2 > days > 0 else ('дня' if 1 < days < 5 else 'дней'))
                        if days == 0:
                            em = "🟢"
                        elif days == 1 and timer.seconds >= 7200:
                            em = "🟡"
                        elif days >= 4 and timer.seconds >= 7200:
                            em = "🔴"

                        time_up = f"{days} {daysstr} и {_time} (серия вышла {time_up})"

                voice = ', '.join(w for w in relese['team']['voice'])
                timing = (' / ' + ', '.join(w for w in relese['team']['timing']) if relese['team']['timing'] else "")
                editing = (' / ' + ', '.join(w for w in relese['team']['editing']) if relese['team']['editing'] else "")
                decor = (' / ' + ', '.join(w for w in relese['team']['decor']) if relese['team']['decor'] else "")
                translator = (' / ' + ', '.join(w for w in relese['team']['translator']) if relese['team']['translator'] else "")
                last_ser = relese['player']['series']['last']
                all_ser = (relese['type']['series'] if relese['type']['series'] is not None else '?')

                mess_dict[relese['season']['week_day']].append(
                    f"""{em}<a href='https://www.anilibria.tv/release/{relese['code']}.html'>{relese['names']['ru']}</a> - ({voice}{timing}{translator}{editing}{decor})\n({last_ser}/{all_ser}) - <b>{time_up}</b>{' <u>РЕЛИЗ ЗАВЕРШЁН!</u>' if last_ser == all_ser else ''}\n""")

        for i in mess_dict:
            mes = ''
            mes += f'<u>{name_week_day(i)}</u>\n\n'
            for s in mess_dict[i]:
                mes += s
            mes += '\n-----------------\n'
            bot.send_message(chat_id=message.chat.id, text=mes, parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True)
    except Exception as err:
        log(f"ERROR {Exception} and {err}", "error")
        bot.send_message(message.chat.id, "Произошла ошибка, отчёт не может быть сформирован")
    finally:
        cur.close()


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    cur = con.cursor()
    if call.data == '1':
        cur.execute(f'''select * from chats where id={call.message.chat.id}''')
        chat = cur.fetchone()
        if chat:
            bot.send_message(chat_id=call.message.chat.id,
                             text='Запись из этого чата уже есть, воспользуйтесь командой /update id')
        else:
            relese_id = call.message.text.split('\n')[1].replace('ID: ', '')
            response = requests.get(f'https://api.anilibria.tv/v2/getTitle?id={relese_id}').json()
            cur.execute(
                f'''insert into chats (id, name, id_relese, code, name_ru, name_en, raw) values ({call.message.chat.id}, "{call.message.chat.title}", {int(relese_id)}, "{response['code']}", "{response['names']['ru']}", "{response['names']['en']}", "SubsPlease");''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Успешно добавлено!✅')

        con.commit()

    elif call.data == '0':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='Тогда перепроверь id и попробуй снова /start id')


thread1 = threading.Thread(target=check, args=[bot, con])
thread1.start()
thread3 = threading.Thread(target=checkTime, args=[bot, con])
thread3.start()

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err:
            if err.args[0] == 'cannot join current thread':
                log(f"ERROR {Exception} and {err}", "error")
                os.abort()
            else:
                time.sleep(200)
