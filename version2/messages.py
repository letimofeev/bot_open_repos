import datetime
from abc import ABCMeta, abstractmethod, ABC

from psycopg2 import sql

from postgres import PostgreSQL as pSQL


class IMessages(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def log_message(self, message_id: int, user_id: int, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_reserved(self, text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_answer_custom(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_answer_photo(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_answer_command(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_days(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_courses(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_groups(self, course_name: str) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_var_num(self, var_num: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def add_answer_custom(self, user_id: int, text: str, answer: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_answer_custom(self, text: str) -> None:
        raise NotImplementedError


class SQLMessages(IMessages):
    """Класс для хранения и получения зарезервированных ответов и сообщений

    Attributes
    ----------
    reserved_words: list
        Дополнительный список зарезервированных сообщений
    courses: list
        Список курсов в текстовом формате
    groups: list
        Список групп в текстовом формате
    days: list
        Список дней недели в текстовом формате
    """
    def __init__(self, table_name=None):
        self.courses = [f"{i + 1} курс" for i in range(4)]
        self.days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
        self.groups = [[f"б03-{group}{i + 1}" for i in range(5)] for group in ["01", "91", "86", "76"]]
        self.var_num_dict = {"1 переменная": 1, "2 переменные": 2}
        self.reserved_words = {}
        self.SQL = pSQL
        self.TableName = table_name

    def log_message(self, message_id, user_id, text):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({message_id}, {user_id}, {text}, {time});
        """).format(
            table_name=sql.Identifier(self.TableName.MESSAGES),  # sql.Identifier нужен для предотвращения SQL инъекций
            message_id=sql.Literal(message_id),
            user_id=sql.Literal(user_id),
            text=sql.Literal(text),
            time=sql.Literal(datetime.datetime.now())
        )
        self.SQL().execute_query(query)

    def is_reserved(self, text: str) -> bool:
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
        pass

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
        query = sql.SQL("""
        SELECT photo_link FROM {table_name}
        WHERE text = {text};
        """).format(
            table_name=sql.Identifier(self.TableName.PHOTO_LINKS),
            text=sql.Literal(text)
        )
        res = self.SQL().execute_read_query(query, one=True)
        if res:
            return res[0]

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
        query = sql.SQL("""
        SELECT answer FROM {table_name}
        WHERE text = {text};
        """).format(
            table_name=sql.Identifier(self.TableName.COMMANDS),
            text=sql.Literal(text)
        )
        res = self.SQL().execute_read_query(query, one=True)
        if res:
            return res[0]

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
        query = sql.SQL("""
        SELECT answer FROM {table_name}
        WHERE text = {text};
        """).format(
            table_name=sql.Identifier(self.TableName.CUSTOM_ANSWERS),
            text=sql.Literal(text)
        )
        res = self.SQL().execute_read_query(query, one=True)
        if res:
            return res

    def add_answer_custom(self, user_id, text, answer):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({user_id}, {text}, {answer})
        ON CONFLICT (text) DO NOTHING;
        """).format(
            table_name=sql.Identifier(self.TableName.CUSTOM_ANSWERS),
            user_id=sql.Literal(user_id),
            text=sql.Literal(text),
            answer=sql.Literal(answer)
        )
        self.SQL().execute_query(query)

    def delete_answer_custom(self, text):
        query = sql.SQL("""
        DELETE FROM {table_name}
        WHERE text = {text};
        """).format(
            table_name=sql.Identifier(self.TableName.CUSTOM_ANSWERS),
            text=sql.Literal(text)
        )
        self.SQL().execute_query(query)

    def get_days(self) -> list:
        """
        Получение списка дней недели

        Returns
        -------
        list
            Список дней недели
        """
        return self.days

    def get_courses(self) -> list:
        """
        Получение списка курсов

        Returns
        -------
        list
            Список курсов
        """
        return self.courses

    def get_groups(self, course_name: str):
        """
        Получение списка групп

        Returns
        -------
        list
            Список групп
        """
        return self.groups[int(course_name[0]) - 1]

    def get_var_num(self, var_num):
        return self.var_num_dict.get(var_num)
