import time
import telebot
from telebot import types
import sqlite3
import requests
import threading
from telegram import ParseMode
from datetime import datetime, timedelta
import os
from utils import name_month, name_week_day, log, convert_to_preferred_format, send_res_rel_time, resetting_requests_gpt
from check_time import checkTime
from reader_RSS import check
from check_status_relise import check_status_relise_in_chats
from decouple import config
import schedule
from ass_to_srt import ass_to_srt
import openai

bot = telebot.TeleBot(config("TOKEN"), parse_mode=None)
con = sqlite3.connect('db.db', check_same_thread=False)
openai.api_key = config("OPENAI_API_KEY")
admin_chat_id = int(config("ADMIN_CHAT_ID"))

max_response_tokens = 250
token_limit = 4096

@bot.message_handler(commands=['start'])
def start(message):
    log(f"send start {message.chat.id, message.chat.username, message.text, message.chat.type}")
    # bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
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


@bot.message_handler(commands=['id'])
def id(message):
    print(message.chat.id)
    print(message)


@bot.message_handler(commands=['kill'])
def stop(message):
    log(f'send stop {message.chat.id, message.chat.username, message.text}')
    bot.send_message(734264203, "АЛЯЯЯРМ!")
    if message.chat.id in [253296124, 734264203, 1625017611, 470092294]:
        bot.send_message(message.chat.id, "Bot is deactivated")
        os.abort()


@bot.message_handler(commands=['raw'])
def set_raw(message):
    log(f'set raw {message}', 'info')
    # bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
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
    bot.send_message(chat_id=734264203, text=("@" + message.chat.username + " - " + message.text + " - " + message.chat.type))
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "📈Ожидайте! формирую отчёт📈")
        cur = con.cursor()
        try:
            response = requests.get(f"https://api.anilibria.tv/v2/getSchedule").json()
            mess_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
            if 'error' not in response:
                for week in response:
                    for relese in week['list']:
                        cur.execute(f'''select * from results where id={relese["id"]}''')
                        res = cur.fetchone()
                        a = datetime.fromtimestamp(relese['updated'])

                        em = "🔘"

                        time_up = f"Последняя серия вышла: {'по расписанию' if week['day'] == a.weekday() else 'не по расписанию'} ({a.day} {name_month(a.month)} {a.hour if a.hour > 9 else f'0{a.hour}'}:{a.minute if a.minute > 9 else f'0{a.minute}'}:{a.second if a.second > 9 else f'0{a.second}'})"

                        if res:
                            if int(res[3]) == -1:
                                time_up = f"Стадия: {res[5] if res[5] != None else 'В работе'}. {time_up}"
                                em = "🎤"
                            else:
                                timer = timedelta(seconds=int(res[3]))
                                days = timer.days
                                _time = convert_to_preferred_format(timer.seconds)
                                daysstr = ('день' if 2 > days > 0 else ('дня' if 1 < days < 5 else 'дней'))
                                if days == 0:
                                    em = "🟢"
                                if days == 1 and timer.seconds <= 7200:
                                    em = "🟢"
                                if days >= 1 and timer.seconds >= 7201:
                                    em = "🟡"
                                if days == 4 and timer.seconds <= 7200:
                                    em = "🟡"
                                if days >= 4 and timer.seconds >= 7201:
                                    em = "🔴"

                                time_up = f"{days} {daysstr} и {_time} ({time_up})"

                        voice = ', '.join(w for w in relese['team']['voice'])
                        timing = (
                            ' / ' + ', '.join(w for w in relese['team']['timing']) if relese['team']['timing'] else "")
                        editing = (' / ' + ', '.join(w for w in relese['team']['editing']) if relese['team'][
                            'editing'] else "")
                        decor = (
                            ' / ' + ', '.join(w for w in relese['team']['decor']) if relese['team']['decor'] else "")
                        translator = (' / ' + ', '.join(w for w in relese['team']['translator']) if relese['team'][
                            'translator'] else "")
                        last_ser = None
                        if relese['player']:
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
            else:
                raise "Что-то не то"
        except Exception as err:
            log(f"ERROR {Exception} and {err}", "error")
            bot.send_message(message.chat.id, "Произошла ошибка, отчёт не может быть сформирован")
        finally:
            con.commit()
            cur.close()


@bot.message_handler(commands=['time'])
def times(message):
    cur = con.cursor()
    cur.execute(f"SELECT * FROM chats WHERE id = {message.chat.id}")
    relese = cur.fetchone()
    if relese:
        timer = convert_to_preferred_format(0)
        response = requests.get(f'https://api.anilibria.tv/v2/getTitle?id={relese[2]}').json()
        if relese[3]:
            log(f"send info message timer {relese[0]}")
            timer = datetime.fromtimestamp(response["updated"]) - datetime.strptime(relese[3], '%Y-%m-%d %H:%M:%S.%f')
        else:
            if message.reply_to_message is None:
                bot.reply_to(message=message, text="В данном чате я не кидала равку, так что ответьте этой же командой на сообщение с вашей равкой")
            else:
                timer = datetime.fromtimestamp(response["updated"]) - datetime.fromtimestamp(message.reply_to_message.date)
        send_res_rel_time(timer, bot, relese, cur, response, con)


@bot.message_handler(commands=['gpt'])
def gpt_request(message):
    try:
        cur = con.cursor()
        count = cur.execute('''select SUM(tt.gpt_count) from team_tg tt;''').fetchone()
        if count[0] < 100:
            user = cur.execute(f"""SELECT * from team_tg where tg_username='@{message.from_user.username}';""").fetchone()
            if user:
                text_gpt = message.text.replace('/gpt ', "")
                if len(text_gpt) > 2:
                    gpt_request_text =[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": text_gpt}
                    ]

                    log(str(gpt_request_text), "info")

                    bot.send_message(message.chat.id, "⌛️Ждём ответ⏳")
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=gpt_request_text
                    )

                    bot.reply_to(message=message, text="\n" + response['choices'][0]['message']['content'] + "\n", parse_mode=ParseMode.MARKDOWN)
                    gpt_count = int(user[3]) + 1
                    cur.execute(f'''UPDATE team_tg SET gpt_count = {gpt_count} where tg_username='@{message.from_user.username}';''')
                    con.commit()
            else:
                bot.reply_to(message=message, text="У тебя не достаточно прав, дабы пользоваться этой командой.\nПропиши /reg <Ник в команде>, что бы получить доступ")
        else:
            bot.reply_to(message=message, text="🧐Закончилось кол-во запросов в неделю, ждите воскресенья 23:00🧐")
    except Exception as err:
        log(f"ERROR {err}", "error")

@bot.message_handler(commands=['reg'])
def reg_new_user(message):
    try:
        if message.chat.type == "private":
            cur = con.cursor()
            user = cur.execute(f"""SELECT * from team_tg where tg_username='@{message.from_user.username}';""").fetchone()
            name_al = message.text.split()[1:]
            if name_al:
                name_al = name_al[0]
                if user:
                    bot.reply_to(message=message, text="Уже зарегистрирован👀")
                else:
                    buttons = [
                        [types.InlineKeyboardButton(text="✅Зарегистрировать✅", callback_data=f'reg_new_user.{message.from_user.username}.{message.chat.id}.{name_al}')],
                        [types.InlineKeyboardButton(text="❌НЕТ❌", callback_data=f'reg_new_user.No.{message.chat.id}')],
                    ]
                    bot.send_message(chat_id=admin_chat_id, text="Регистрация нового пользователя: @{0}".format(message.from_user.username), reply_markup=types.InlineKeyboardMarkup(buttons))
                    bot.reply_to(message=message, text="Ожидай пока сахар соизволит подтвердить👀")
            else:
                bot.reply_to(message=message, text="А ник твой на проекте, нам самим гадать?)\n(пример /reg Caxaro4ek)")
        else:
            bot.reply_to(message=message, text="🐙Только в лс...🐙")
    except Exception as err:
        log(f"ERROR {err}", "error")


@bot.message_handler(commands=['unreg'])
def reg_new_user(message):
    if message.chat.id == admin_chat_id:
        username = message.text.split()[1:][0]
        cur = con.cursor()
        user = cur.execute("""SELECT * from team_tg where tg_username='@{0}';""".format(username)).fetchone()
        if user:
            cur.execute("""delete from team_tg where id={0};""".format(user[0]))
            con.commit()
            bot.reply_to(message=message, text="Пользователь @{0} удалён".format(username))
        else:
            bot.reply_to(message=message, text="Пользователя @{0} не существует".format(username))


@bot.message_handler(commands=['editstatus'])
def editstatus(message):
    buttons = [
        [types.InlineKeyboardButton(text="Перевод/редактура", callback_data=f'translation.{message.chat.id}')],
        [types.InlineKeyboardButton(text="Озвучка", callback_data=f'voiceover.{message.chat.id}')],
        [types.InlineKeyboardButton(text="Тайминг/фиксы", callback_data=f'timing.{message.chat.id}')],
        [types.InlineKeyboardButton(text="Сборка", callback_data=f'assembling.{message.chat.id}')]
    ]
    bot.send_message(message.chat.id, f'Каков статус релиза?', reply_markup=types.InlineKeyboardMarkup(buttons))


@bot.message_handler(commands=['subready'])
def sub_is_ready(message):
    try:
        cur = con.cursor()
        time_alert = cur.execute(f"""SELECT time_alerts  from chats c where id={message.chat.id};""").fetchone()
        if time_alert:
            time_ready_sub = datetime.now() - datetime.strptime(time_alert[0], "%Y-%m-%d %H:%M:%S.%f")
        else:
            if message.reply_to_message is None:
                bot.reply_to(message=message, text="В данном чате я не кидала равку, так что ответьте этой же командой на сообщение с вашей равкой")
            else:
                time_ready_sub = datetime.now() - datetime.fromtimestamp(message.reply_to_message.date)
        daysstr = ('день' if 2 > time_ready_sub.days > 0 else ('дня' if 1 < time_ready_sub.days < 5 else 'дней'))
        time = convert_to_preferred_format(time_ready_sub.seconds)
        bot.reply_to(message=message, text=f"🖋Саб вышел за: {time_ready_sub.days} {daysstr} и {time}✒️")
    except Exception as ex:
        log(ex, "error")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    try:
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
        elif call.data == '0':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Тогда перепроверь id и попробуй снова /start id')
        elif "translation" in call.data:
            cur.execute(f'''UPDATE results SET status = "Перевод/редактура" WHERE chat={call.data.split(".")[1]};''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Статус: "Перевод/редактура"✅\n(если вы ошиблись пропишите /editstatus)')
        elif "voiceover" in call.data:
            cur.execute(f'''UPDATE results SET status = "Озвучка" WHERE chat={call.data.split(".")[1]};''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Статус: "Озвучка"✅\n(если вы ошиблись пропишите /editstatus)')
        elif "timing" in call.data:
            cur.execute(f'''UPDATE results SET status = "Тайминг/фиксы" WHERE chat={call.data.split(".")[1]};''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Статус: "Тайминг/фиксы"✅\n(если вы ошиблись пропишите /editstatus)')
        elif "assembling" in call.data:
            cur.execute(f'''UPDATE results SET status = "Сборка" WHERE chat={call.data.split(".")[1]};''')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅Статус: "Сборка"\n(если вы ошиблись пропишите /editstatus)')
        elif "reg_new_user" in call.data:
            if call.data.split(".")[1] != "No":
                cur.execute(f'''insert into team_tg (tg_username, al_name) values ("@{call.data.split(".")[1]}", "{call.data.split(".")[3]}")''')
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='✅@{0} зарегистрирован✅'.format(call.data.split(".")[1]))
                bot.send_message(chat_id=int(call.data.split(".")[2]), text="Подтвердил☺️ Пользуйся!")
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='😎Ну нет, так нет😎')
                bot.send_message(chat_id=int(call.data.split(".")[2]), text="❌Не подтвердил❌ (либо он промахнулся по кнопке, либо ты не либриец...) Попробуй ещё раз)")
    except Exception as err:
        log(f"ERROR {err}", "error")
    finally:
        con.commit()


@bot.message_handler(commands=['srt'])
def convert_sub(message: types.Message):
    try:
        message.reply_to_message.document.file_id
    except Exception as err:
        log(f"ERROR {err}", "error")
        bot.send_message(message.chat.id, "Команда работает реплаем на сообщение с сабом")
        return

    file_info = bot.get_file(message.reply_to_message.document.file_id)
    file_name = message.reply_to_message.document.file_name

    if file_name.endswith('.ass'):
        file_in_bytes = bot.download_file(file_info.file_path)
        srt_file = ass_to_srt(file_in_bytes, file_name)
        bot.send_document(message.chat.id, srt_file)
    else:
        bot.send_message(message.chat.id, "неизвестный формат")


def schedules():
    schedule.every(3).minutes.do(lambda: check(bot, con))
    schedule.every(3).minutes.do(lambda: checkTime(bot, con))
    schedule.every().sunday.at("16:30").do(lambda: check_status_relise_in_chats(bot, con))
    schedule.every().sunday.at("23:00").do(lambda: resetting_requests_gpt(con))
    while True:
        schedule.run_pending()


thread1 = threading.Thread(target=schedules)
thread1.start()

# thread1 = threading.Thread(target=check, args=[bot, con])
# thread1.start()
# thread3 = threading.Thread(target=checkTime, args=[bot, con])
# thread3.start()

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err:
            if err.args[0] == 'cannot join current thread':
                log(f"ERROR {Exception} and {err}", "error")
            else:
                time.sleep(200)
