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


def check(bot, con):
    while True:
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
            max_last_time = last_time
            for i in list_title:
                if i['pubDate'] > last_time:
                    if i['pubDate'] > max_last_time:
                        max_last_time = i['pubDate']
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
                            cur.execute(f'''update chats set time_alerts='{datetime.now()}' where id_relese={f[2]}''')
                            cur.execute(f'''update results set time=-1 where id={f[2]}''')
            time.sleep(120)
        except Exception as err:
            log(f"ERROR {Exception} and {err}", "error")
            time.sleep(100)
        finally:
            con.commit()
            cur.close()
