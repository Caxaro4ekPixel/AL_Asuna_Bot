import time
import telebot
from telebot import types
import sqlite3
import requests
import difflib
import xmltodict
import threading
from dateutil.parser import parse
import calendar
import io
from telegram import ParseMode
from datetime import datetime, timedelta
import logging
import re
import os


def log(mess, log_type='info'):
    logging.basicConfig(filename='logging file.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level='INFO')
    if log_type == 'info':
        logging.info(mess)
    elif log_type == 'error':
        logging.error(mess)


bot = telebot.TeleBot("5232964507:AAFANCtpnMIHK0Us73C8idPYDmpQcfnZ88M", parse_mode=None)


@bot.message_handler(commands=['start'])
def start(message):
    log(f"send start {message.chat.id, message.chat.username, message.text}")
    bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
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
    bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        con = sqlite3.connect('db.db')
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
        con.close()
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
    bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        try:
            con = sqlite3.connect('db.db')
            cur = con.cursor()
            raw = message.text.replace("/raw ", "")
            if '/raw' in raw:
                bot.send_message(message.chat.id, "❌Некоректно введено название❌")
            else:
                cur.execute(f'''update chats set raw='{raw}' where id = {message.chat.id};''')
                con.commit()
                bot.send_message(message.chat.id, f'✅Успешно изменено на "{raw}"✅')
                cur.close()
                con.close()
        except:
            log(f'error set raw {message}', 'error')
    else:
        bot.send_message(message.chat.id, 'Не ТроЖ бота в лс)')


def name_week_day(week_day):
    day = ""
    if week_day == 0:
        day = "Понедельник"
    elif week_day == 1:
        day = "Вторник"
    elif week_day == 2:
        day = "Среда"
    elif week_day == 3:
        day = "Четверг"
    elif week_day == 4:
        day = "Пятница"
    elif week_day == 5:
        day = "Суббота"
    elif week_day == 6:
        day = "Воскресенье"

    return day


@bot.message_handler(commands=['report'])
def result(message):
    log(f'get report {message.chat.id}, {message.chat.username}, {message.chat.type}', 'info')
    bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    bot.send_message(message.chat.id, "📈Ожидайте! формирую отчёт📈")
    try:
        con = sqlite3.connect('db.db')
        cur = con.cursor()
        response = requests.get(f"https://api.anilibria.tv/v2/getSchedule").json()
        mess_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for week in response:
            for relese in week['list']:
                cur.execute(f'''select * from results where id={relese["id"]}''')
                res = cur.fetchone()
                time_up = datetime.fromtimestamp(relese['updated'])
                if res:
                    time_up = res[3] + f" (серия вышла {time_up})"
                voice = ', '.join(w for w in relese['team']['voice'])
                timing = ', '.join(w for w in relese['team']['timing'])
                editing = ', '.join(w for w in relese['team']['editing'])
                decor = ', '.join(w for w in relese['team']['decor'])
                translator = ', '.join(w for w in relese['team']['translator'])
                last_ser = relese['player']['series']['last']
                all_ser = (relese['type']['series'] if relese['type']['series'] is not None else '?')

                mess_dict[relese['season']['week_day']].append(f"""<a href='https://www.anilibria.tv/release/{relese['code']}.html'>{relese['names']['ru']}</a> - ({voice} / {timing} / {translator} / {editing} / {decor})\n({last_ser}/{all_ser}) - <b>{time_up}</b>{' <u>РЕЛИЗ ЗАВЕРШЁН!</u>' if last_ser == all_ser else ''}\n""")

        for i in mess_dict:
            mes = ''
            mes += f'<u>{name_week_day(i)}</u>\n\n'
            for s in mess_dict[i]:
                mes += s
            mes += '\n-----------------\n'
            bot.send_message(chat_id=message.chat.id, text=mes, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as err:
        log(f"ERROR {Exception} and {err}", "error")
        bot.send_message(message.chat.id, "Произошла ошибка, отчёт не может быть сформирован")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == '1':

        con = sqlite3.connect('db.db')
        cur = con.cursor()
        cur.execute(f'''select * from chats where id={call.message.chat.id}''')
        chat = cur.fetchone()
        if chat:
            bot.send_message(chat_id=call.message.chat.id,
                             text='Запись из этого чата уже есть, воспользуйтесь командой /update id')
        else:
            relese_id = call.message.text.split('\n')[1].replace('ID: ', '')
            response = requests.get(f'https://api.anilibria.tv/v2/getTitle?id={relese_id}').json()
            cur.execute(f'''insert into chats (id, name, id_relese, code, name_ru, name_en, raw) values ({call.message.chat.id}, "{call.message.chat.title}", {int(relese_id)}, "{response['code']}", "{response['names']['ru']}", "{response['names']['en']}", "SubsPlease");''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Успешно добавлено!✅')

        con.commit()
        cur.close()
        con.close()

    elif call.data == '0':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='Тогда перепроверь id и попробуй снова /start id')


def normolize_text(s):
    a = []
    for i in re.sub(r'\(.*\)', '', re.sub(r'\[[^\]]+\]', '', s)).split(' '):
        if i != '':
            a.append(i)
    b = []
    for i in a:
        if not re.search(r'\d', i) and '.mkv' not in i and '-' != i:
            b.append(i)
    nor_s = (' '.join(i for i in b))
    return nor_s


def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def check():
    while True:
        con = sqlite3.connect('db.db')
        cur = con.cursor()
        try:
            log(f"start check new sub")
            cur.execute('''SELECT * FROM lastReles''')

            response = requests.get(f'https://nyaa.si/?page=rss&f=2&c=1_2')
            dict_list = xmltodict.parse(response.text)['rss']['channel']['item']

            last_time = cur.fetchone()[1]
            list_title = []
            for i in dict_list:
                list_title.append({
                    'title': i['title'],
                    'link': i['link'],
                    'pubDate': calendar.timegm(parse(i['pubDate']).utctimetuple()),
                    'size': i['nyaa:size']
                })

            alerts_list = {}
            max = last_time
            for i in list_title:
                if i['pubDate'] > last_time:
                    if i['pubDate'] > max:
                        max = i['pubDate']
                        cur.execute(f'''UPDATE lastReles set date={i['pubDate']} WHERE id=1''')
                    a = normolize_text(i['title'])
                    alerts_list[a] = []
                else:
                    break

            for i in list_title:
                if i['pubDate'] > last_time:
                    a = normolize_text(i['title'])
                    alerts_list[a].append({
                        'title': i['title'],
                        'link': i['link'],
                        'pubDate': i['pubDate'],
                        'size': i['size']
                    })
                else:
                    break

            alerts = []
            cur.execute('''SELECT * FROM chats''')
            chats = cur.fetchall()
            for i in alerts_list:
                for f in chats:
                    if similarity(i, f[4].replace('-', ' ')) > 0.70:

                        file_list = []
                        log(f"new sub {alerts_list[i]}")

                        temp = str(f[5]) + ' / ' + str(f[6]) + '\n\n<a href="https://www.anilibria.tv/release/' + f[
                            4] + '.html">Сайт</a> ... <a href="https://backoffice.anilibria.top/resources/release-resources/' + str(
                            f[2]) + '">Админка</a>'

                        temp = temp + "\n\n"
                        for j in alerts_list[i]:
                            if f[7].lower() in j['title'].lower() and 'hevc' not in j['title'].lower():
                                response = requests.get(j['link'], allow_redirects=True)
                                file = io.BytesIO()
                                file.write(response.content)
                                file.seek(0, 0)
                                quality = '1080p'
                                if '480p' in j['title']:
                                    quality = '480p'
                                if '540p' in j['title']:
                                    quality = '540p'
                                elif '720p' in j['title']:
                                    quality = '720p'
                                elif '1080p' in j['title']:
                                    quality = '1080p'
                                file.name = quality + '_' + str(f[5]) + '.torrent'
                                file_list.append(types.InputMediaDocument(file))

                                temp = temp + '◢◤<a href="' + j['link'] + '">[' + quality + ' - ' + str(
                                    j['size']) + ']</a>◥◣\n'
                        temp = temp + "\n\n#NewSub"
                        alerts.append([temp, file_list, f[2]])

            for i in alerts:
                for f in chats:
                    if i[2] == f[2]:
                        if i[1]:
                            log(f"send info message in chat {f[0]} relese {f[2]}")
                            mess = bot.send_message(f[0], i[0], parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                            bot.send_message(734264203, i[0], parse_mode=ParseMode.HTML, disable_web_page_preview=True)

                            try:
                                bot.pin_chat_message(chat_id=f[0], message_id=mess.message_id)
                            except:
                                pass
                            bot.send_media_group(f[0], i[1])
                            cur.execute(f'''update chats set time_alerts='{datetime.now()}' where id={f[0]} and id_relese={f[2]}''')
            time.sleep(120)
        except Exception as err:
            log(f"ERROR {Exception} and {err}", "error")
            time.sleep(100)
        finally:
            con.commit()
            cur.close()
            con.close()


def convert_to_preferred_format(sec):
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    min = sec // 60
    sec %= 60
    return "%02d:%02d:%02d" % (hour, min, sec)


def checkTime():
    while True:
        try:
            con = sqlite3.connect('db.db')
            cur = con.cursor()
            cur.execute('SELECT * FROM lastTimeUpdates')
            _time = cur.fetchone()
            response = requests.get(f'https://api.anilibria.tv/v2/getUpdates?since={_time[1]}&limit=100').json()
            if response:
                last_up = response[0]["updated"] + 1
                for i in response:
                    cur.execute(f'SELECT * FROM chats WHERE id_relese = {i["id"]}')
                    relese = cur.fetchone()
                    if relese:
                        if relese[3]:
                            log(f"send info message timer {relese[0]}")
                            timer = datetime.fromtimestamp(i["updated"]) - datetime.strptime(relese[3],
                                                                                             '%Y-%m-%d %H:%M:%S.%f')
                            days = timer.days
                            _time = convert_to_preferred_format(timer.seconds)
                            daysstr = ('день' if 2 > days > 0 else ('дня' if 1 < days < 5 else 'дней'))
                            if days >= 0:
                                # 734264203 relese[0]
                                bot.send_message(chat_id=734264203, text=f"🕘Серия вышла за:🕘\n{days} {daysstr} и {_time}\n\n#Time")
                                cur.execute(f'''select * from results where chat = {relese[0]}''')
                                temp = cur.fetchone()
                                if temp:
                                    cur.execute(f'''update results set time = "{days} {daysstr} и {_time}", last_up = {last_up} where id = {temp[0]}''')
                                else:
                                    cur.execute(f'''insert into results ('id', 'chat', 'relese', 'time', 'last_up') values ({i["id"]} ,{relese[0]}, "{relese[5]}", "{days} {daysstr} и {_time}", {i["updated"]})''')
                cur.execute(f'UPDATE lastTimeUpdates SET timestamp = {last_up}')
                con.commit()
                cur.close()
                con.close()
            time.sleep(50)
        except Exception as err:
            log(f"ERROR {Exception} and {err}", "error")
            time.sleep(100)


# thread1 = threading.Thread(target=check)
# thread1.start()
# thread3 = threading.Thread(target=checkTime)
# thread3.start()

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
