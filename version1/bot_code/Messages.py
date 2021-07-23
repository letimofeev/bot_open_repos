from Settings import *
import distance
from abc import ABCMeta, abstractmethod, ABC


class IMessages(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_in_reserve(self, text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_teacher_id(self, text: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_answer_custom(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_answer_photo(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_answer_command(self, text):
        raise NotImplementedError

    @abstractmethod
    def get_days(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_courses(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_start(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_groups(self) -> [str]:
        raise NotImplementedError


class PandasMessages(IMessages):
    """Класс для хранения и получения зарезервированных ответов и сообщений

    Attributes
    ----------
    photos: pandas.core.frame.DataFrame
        Pandas таблица с ссылками на изображения
    commands: pandas.core.frame.DataFrame
        Pandas таблица с ответами на команды
    custom: pandas.core.frame.DataFrame
        Pandas таблица с ответами на сообщения, установленные пользователями
    reserved_words: list
        Дополнительный список зарезервированных сообщений
    __courses: list
        Список курсов в текстовом формате
    __groups: list
        Список групп в текстовом формате
    __days: list
        Список дней недели в текстовом формате
    __start: list
        Список кнопок в стартовой клавиатуре в текстовом формате


    """
    def __init__(self, photo_links=None, commands=None, custom=None):
        self.photos = photo_links
        self.commands = commands
        self.custom = custom
        self.__courses = [f"{i + 1} курс" for i in range(Constants.courses_count.value)]
        self.__days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
        self.__start = ["расписание", "лекции", "лабы", "подготовка к письменному госу по математике"]
        self.__groups = [[f"б03-{group}{i + 1}" for i in range(Constants.groups_count.value)] for group in
                         ["01", "91", "86", "76"]]
        self.reserved_words = self.__courses + self.__days + self.__start + self.__groups[0] + self.__groups[1] + \
                              self.__groups[2] + self.__groups[3] + ['/help', "мат. логика", "комп. технологии (л)",
                                                                     "общая физика: оптика (л)",
                                                                     "общая физика: оптика (с)",
                                                                     "колебания и волны (с)", "колебания и волны (л)",
                                                                     "основы прочности (с)", "основы прочности (л)",
                                                                     "аэродинамика (л)", "аналитическая механика (л)",
                                                                     "теория вероятности", "дифф. уравнения (с)",
                                                                     "дифф. уравнения (л)", "гармонический анализ (с)",
                                                                     "гармонический анализ (л)", "обучить бота",
                                                                     "изменить данные"]

    def is_in_reserve(self, text: str) -> bool:
        """
        Проверка является ли текст в списке зарезервированных фраз

        Parameters
        ----------
        text: str
            Текст, который нужно проверить

        Returns
        -------
        bool
            True если содержится, False иначе
        """
        valid = True
        valid &= distance.levenshtein(text[:6], 'запрос ') > Constants.levenshtein_dist.value
        valid &= distance.levenshtein(text[:6], 'график ') > Constants.levenshtein_dist.value
        for word in self.reserved_words:
            valid &= distance.levenshtein(text, word) > Constants.levenshtein_dist.value
        return not valid

    def get_teacher_id(self, text: str) -> int:
        """
        Получение id пользователя, добавившего фразу

        Parameters
        ----------
        text: str
            Сообщение, ответ на которое добавил пользователь

        Returns
        -------
        int
            id пользователя
        """
        return self.custom[self.custom['Q'] == text]['user_id'].values[0]

    def get_answer_custom(self, text: str) -> str:
        """
        Получение ответа на текстовое сообщение

        Parameters
        ----------
        text: str
            Сообщение, на которое нужно ответить

        Returns
        -------
        str
            Ответ на сообщение
        """
        return self.custom[self.custom['Q'] == text]['A'].values[0]

    def get_answer_photo(self, text: str) -> str:
        """
        Получение ссылки на фотографию

        Parameters
        ----------
        text: str
            Сообщение, на которое нужно ответить

        Returns
        -------
        str
            Ссылка на фотографию
        """
        return self.photos[text][0]

    def get_answer_command(self, text: str) -> str:
        """
        Получение ответа на комманду

        Parameters
        ----------
        text: str
            Команда, на которую нужно ответить

        Returns
        -------
        str
            Ответ на команду
        """
        return self.commands[text][0]

    def get_days(self) -> list:
        """
        Получение списка дней недели

        Returns
        -------
        list
            Список дней недели
        """
        return self.__days

    def get_courses(self) -> list:
        """
        Получение списка курсов

        Returns
        -------
        list
            Список курсов
        """
        return self.__courses

    def get_start(self) -> list:
        """
        Получение списка стартовых сообщений

        Returns
        -------
        list
            Список стартовых сообщений
        """
        return self.__start

    def get_groups(self):
        """
        Получение списка групп

        Returns
        -------
        list
            Список групп
        """
        return self.__groups

