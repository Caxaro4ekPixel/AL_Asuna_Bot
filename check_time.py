from datetime import datetime
import requests
from utils import log, convert_to_preferred_format
import time


def checkTime(bot, con):
    while True:
        cur = con.cursor()
        try:
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
                            timer = datetime.fromtimestamp(i["updated"]) - datetime.strptime(relese[3], '%Y-%m-%d %H:%M:%S.%f')
                            days = timer.days
                            _time = convert_to_preferred_format(timer.seconds)
                            daysstr = ('день' if 2 > days > 0 else ('дня' if 1 < days < 5 else 'дней'))
                            if days >= 0:
                                # 734264203 relese[0]
                                bot.send_message(chat_id=relese[0], text=f"🕘Серия вышла за:🕘\n{days} {daysstr} и {_time}\n\n#Time")
                                cur.execute(f'''select * from results where chat = {relese[0]}''')
                                temp = cur.fetchone()
                                if temp:
                                    cur.execute(f'''update results set time = "{(timer.days*86400) + timer.seconds}", last_up = {last_up} where id = {temp[0]}''')
                                else:
                                    cur.execute(f'''insert into results ('id', 'chat', 'relese', 'time', 'last_up') values ({i["id"]} ,{relese[0]}, "{relese[5]}", "{days} {daysstr} и {_time}", {i["updated"]})''')
                cur.execute(f'UPDATE lastTimeUpdates SET timestamp = {last_up}')
            time.sleep(50)
        except Exception as err:
            log(f"ERROR {Exception} and {err}", "error")
            time.sleep(100)
        finally:
            con.commit()
            cur.close()
