from .chat import Chat
from .user import User
from .bot_conf import BotConfig, NyaaRssConf, AlApiConf
from .file import File
from .gpt import ChatGPT
from .log import Log
from .release import Release
from .episode import Episode, Torrent

__beanie_models__ = [Chat, User, Release, BotConfig, File, ChatGPT, Log]