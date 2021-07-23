from Wolframalpha import WolframalphaAPI
from FileLoader import PandasLoader
from Links import PandasLink
from Schedule import PandasSchedule
from Messages import PandasMessages
from Storage import GoogleAPI
from typing import NamedTuple
from Keyboard import VkKeyboard, TgKeyboard
from Saver import PandasSaver


class Configuration(NamedTuple):
    BotPlatform = "VKBot"
    if BotPlatform == "VKBot":
        prefix = "vk_"
        Keyboard = VkKeyboard
    elif BotPlatform == "TGBot":
        prefix = "tg_"
        Keyboard = TgKeyboard
    FileLoader = PandasLoader
    Links = PandasLink
    Schedule = PandasSchedule
    Messages = PandasMessages
    Storage = GoogleAPI
    QueryResponder = WolframalphaAPI
    GraphBuilder = WolframalphaAPI
    python_version = "python3.9"
    Saver = PandasSaver
