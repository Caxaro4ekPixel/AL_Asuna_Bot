import csv
from asuna_bot.db.odm import Chat, Release, User
from asuna_bot.db.odm.chat import ChatConfig




def create_chat_list():
    new_chats = []
    chat_file = open("chats.csv", encoding='utf8')
    chats = csv.reader(chat_file)

    for chat in chats:
        chat_id = int(chat[0])
        status = None
        name = chat[1]
        release = chat[2]

        new_config = ChatConfig(submitter=chat[7])
        new_chat = Chat(id=chat_id, status=status, name=name, config=new_config, release=release)
        new_chats.append(new_chat)
    
    return new_chats


def create_user_list():
    new_users = []
    with open("parsed_members.txt", 'r', encoding='utf8') as file:
        users = file.readlines()
        for user in users:
            _id = user.split(" / ")[0]
            name = user.split(" / ")[1]
            roles = user.split(" / ")[2].strip().replace(" ", "").split(",")
            new_user = User(id=_id, name=name, role=roles)
            new_users.append(new_user)

    return new_users


def create_release_list():
    new_releases = []
    chat_file = open("chats.csv", encoding='utf8')
    chats = csv.reader(chat_file)

    for chat in chats:
        rel_id = chat[2]
        chat_id = chat[0]
        code = chat[4]

        en_title = chat[6]
        ru_title = chat[5]
        new_release = Release(
            id=rel_id, 
            chat_id=chat_id, 
            code=code, 
            en_title=en_title, 
            ru_title=ru_title, 
            last_update=1624984055
        )
        new_releases.append(new_release)

    return new_releases