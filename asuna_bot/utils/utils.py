
from datetime import timedelta
import json
import random

def craft_time_str(td: timedelta) -> str:
    match td.days:
        case 0: 
            days = ""
        case 1 | 21 | 31 | 41:
            days = f"{td.days} день"
        case 2 | 3 | 4 | 22 | 23 | 24 | 32 | 33 | 34:
            days = f"{td.days} дня"
        case _:
            days = f"{td.days} дней"

    h = int(td.seconds // 3600)
    match h:
        case 0: 
            hours = ""
        case 1 | 21:
            hours = f"{h} час"
        case 2 | 3 | 4 | 22 | 23:
            hours = f"{h} часа"
        case _:
            hours = f"{h} часов"

    m = int((td.seconds // 60) % 60)
    match m:
        case 0:
            minutes = ""
        case 1 | 21 | 31 | 41 | 51:
            minutes = f"{m} минуту"
        case 2 | 3 | 4 | 22 | 23 | 24 | 32 | 33 | 34 | 42 | 43 | 44 | 52 | 53 | 54:
            minutes = f"{m} минуты"
        case _:
            minutes = f"{m} минут"
    
    return f"{days} {hours} {minutes}".strip()

def random_kaomoji() -> str:
    with open('emoticon_dict.json', 'r', encoding='utf-8') as f:
        emoticon_dict = json.load(f)
        kaomoji = list(emoticon_dict.keys())

    rnd = random.randint(0, len(kaomoji) - 1)
    return kaomoji[rnd]