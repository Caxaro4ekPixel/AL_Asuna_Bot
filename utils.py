import difflib
import re
import logging


def name_week_day(week_day):
    day = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
    return day[week_day]


def name_month(mon_day):
    month_name = {1: 'янв', 2: 'фев', 3: 'мар', 4: 'апр', 5: 'май', 6: 'июн', 7: 'июл', 8: 'авг', 9: 'сен', 10: 'окт', 11: 'ноя', 12: 'дек'}
    return month_name[mon_day]


def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


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


def log(mess, log_type='info'):
    logging.basicConfig(filename='logging file.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level='INFO')
    if log_type == 'info':
        logging.info(mess)
    elif log_type == 'error':
        logging.error(mess)


def convert_to_preferred_format(sec):
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    min = sec // 60
    sec %= 60
    return "%02d:%02d:%02d" % (hour, min, sec)
