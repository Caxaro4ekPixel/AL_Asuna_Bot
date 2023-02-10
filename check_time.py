from datetime import datetime
import requests
from utils import log, send_res_rel_time
import time


def checkTime(bot, con):
    cur = con.cursor()
    print("maybe work")
    try:
        cur.execute('SELECT * FROM lastTimeUpdates')
        _time = cur.fetchone()
        print(_time, datetime.now())
        response = requests.get(f'http://api.anilibria.tv/v2/getUpdates?since={_time[1]}&limit=100',
                                verify=False).json()
        print(response)
        if 'error' not in response:
            if response:
                cur.execute(f'UPDATE lastTimeUpdates SET timestamp = {response[0]["updated"] + 1}')
                for i in response:
                    cur.execute(f'SELECT * FROM chats WHERE id_relese = {int(i["id"])}')
                    relese = cur.fetchone()
                    if relese:
                        if relese[3]:
                            log(f"send info message timer {relese[0]}")
                            timer = datetime.fromtimestamp(i["updated"]) - datetime.strptime(relese[3], '%Y-%m-%d %H:%M:%S.%f')
                            send_res_rel_time(timer, bot, relese, cur, i, con)
        else:
            log(f"ERROR {response}", "error")
    except Exception as err:
        log(f"ERROR {Exception} and {err}", "error")
    finally:
        con.commit()
        cur.close()
