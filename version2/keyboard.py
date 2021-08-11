import json
import enum
import ast
from abc import ABC, abstractmethod

import telebot as tb



class IKeyboard(ABC):
    """
    Интерфейс для класса клавиатуры
    """
    @abstractmethod
    def add_buttons(self, labels: list, colors: list) -> None:
        raise NotImplementedError

    @abstractmethod
    def to_json(self, name: str) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def json_to_keyboard(name: str) -> "keyboard":
        pass


class VkKeyboard(IKeyboard):
    """Класс VkKeyboard используется для создания клавиатуры vk

    Attributes
    ----------
    labels: list
        Текст, который будет на кнопках. Подаётся в виде списка, содержащего строки и списки строк.
        Внутренние списки будут создавать кнопки, располагающиеся на одной линии.
    colors: list
        Цвета кнопок. Подаются в формате, идентичном labels
    one_time: bool
        Если True, то клавиатура будет скрываться сразу после нажатия на неё
    inline: bool
        Если True, то клавиатура будет подана внутри сообщения
    """
    def __init__(self, labels=None, colors=None, one_time=False, inline=False):
        if inline:
            self.keyboard = {"inline": inline, "buttons": []}
        else:
            self.keyboard = {"one_time": one_time, "buttons": []}
        self.add_buttons(labels, colors)

    def add_buttons(self, labels: list = None, colors: list = None) -> None:
        """
        Функция добавления кнопок в клавиатуру

        Parameters
        ----------
        labels: list, default None
            См. описание __init__
        colors: list, default None
            См. описание __init__

        Returns
        -------
        None
        """
        for label, color in zip(labels, colors):
            if type(label) == str:
                self.keyboard["buttons"].append([{"action": {"type": "text", "label": label}, "color": color}])
            else:
                self.keyboard["buttons"].append(
                    [{"action": {"type": "text", "label": i}, "color": j} for i, j in zip(label, color)])

    def to_json(self, name: str) -> None:
        """
        Метод создания клавиатуры из объекта класса VkKeyboard в json файл

        Parameters
        ----------
        name: str
            Полное имя выходного json файла (например 'test.json')

        Returns
        -------
        None
        """
        with open(name, "w", encoding="utf-8") as keyboard_file:
            json.dump(self.keyboard, keyboard_file)

    @staticmethod
    def json_to_keyboard(name: str) -> str:
        """
        Конвертация json файла в объект, который можно подать в качестве аргумента в методе отправки сообщения

        Parameters
        ----------
        name: str
            Название json файла с клавиатурой

        Returns
        -------
        str
            Имя файла
        """
        return name


class VkColors(enum.Enum):
    """
    Enum class с цветами клавиатур vk
    """
    green = 'positive'
    red = 'negative'
    blue = 'primary'
    white = 'secondary'


class TgKeyboard(IKeyboard):
    """Класс TgKeyboard используется для создания клавиатуры telegram

    Attributes
    ----------
    labels: list
        Текст, который будет на кнопках. Подаётся в виде списка, содержащего строки и списки строк.
        Внутренние списки будут создавать кнопки, располагающиеся на одной линии.
    inline: bool
        Если True, то клавиатура будет подана внутри сообщения
    """
    def __init__(self, labels=None, inline=False):
        if inline:
            self.keyboard = tb.types.InlineKeyboardMarkup()
        else:
            self.keyboard = tb.types.ReplyKeyboardMarkup(True)
        self.add_buttons(labels, inline=inline)

    def add_buttons(self, labels: list, inline=False, colors=None) -> None:
        """
        Функция добавления кнопок в клавиатуру

        Parameters
        ----------
        labels: list, default None
            См. описание __init__
        colors: list, default None
            См. описание __init__
        inline: bool
            См. описание __init__

        Returns
        -------
        None
        """
        if inline:
            for i in labels:
                if type(i) == str:
                    self.keyboard.add(tb.types.InlineKeyboardButton(text=i, callback_data=i))
                else:
                    labs = [tb.types.InlineKeyboardButton(text=label, callback_data=label) for label in i]
                    self.keyboard.add(*labs)
        else:
            for label in labels:
                if type(label) == str:
                    self.keyboard.row(label)
                else:
                    self.keyboard.row(*label)

    def to_json(self, name: str) -> None:
        """
        Метод создания клавиатуры из объекта класса TgKeyboard в json файл

        Parameters
        ----------
        name: str
            Полное имя выходного json файла (например 'test.json')

        Returns
        -------
        None
        """
        kb = ast.literal_eval(self.keyboard.to_json().replace('true', 'True').replace('false', 'False'))
        with open(name, "w", encoding="utf-8") as keyboard_file:
            json.dump(kb, keyboard_file)

    @staticmethod
    def json_to_keyboard(name: str) -> "TgKeyboard.keyboard":
        """
        Конвертация json файла в объект, который можно подать в качестве аргумента в методе отправки сообщения

        Parameters
        ----------
        name: str
            Название json файла с клавиатурой

        Returns
        -------
        TgKeyboard().keyboard
            Клавиатура telegram
        """
        with open(name) as keyboard_file:
            _dict = json.load(keyboard_file)
            labels = [[list(_dict.values())[0][i][j]['text'] for j in range(len(list(_dict.values())[0][i]))] for i in range(len(list(_dict.values())[0]))]
            inline = False if list(_dict.keys())[0] == 'keyboard' else True
            return TgKeyboard(labels=labels, inline=inline).keyboard
