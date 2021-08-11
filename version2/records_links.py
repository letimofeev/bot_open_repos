from abc import ABCMeta, abstractmethod, ABC

from file_loader import PandasLoader


class ILink(ABC):
    """
    Интерфейс класса для получения ссылок
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_subj_list(self) -> [str]:
        raise NotImplementedError

    @abstractmethod
    def get_subj_link(self, subj_name: str) -> str:
        raise NotImplementedError


class PandasLink:
    """
    Класс для получения ссылок на занятия из файла

    Attributes
    ----------
    links: pandas.core.frame.DataFrame
        Pandas таблица с ссылками
    """
    def __init__(self, course_name, folder_name=None):
        self.links = PandasLoader().get_csv(file_name=course_name, folder_name=folder_name)
        self.normalize_subj_names()

    def normalize_subj_names(self) -> None:
        """
        Приведение названий предметов к нижнему регистру

        Returns
        -------
        None
        """
        subj_name_key = self.links.columns[0]
        self.links[subj_name_key] = \
            [self.links[subj_name_key].values[i].lower() for i in range(self.links[subj_name_key].values.shape[0])]

    def get_subj_list(self) -> list:
        """
        Получение списка названий предметов

        Returns
        -------
        list
            Список предметов
        """
        if self.links is None:
            return []
        subj_name_key = self.links.columns[0]
        subj_list = self.links[subj_name_key].tolist()
        return subj_list

    def get_subj_link(self, subj_name: str) -> str:
        """
        Получение ссылки на предмет

        Parameters
        ----------
        subj_name: str
            Название предмета, ссылку на который нужно получить
        Returns
        -------
        str
            Ссылка на плейлист
        """
        if self.links is None:
            return "Error"
        subj_name_key, subj_link_key = self.links.columns[0], self.links.columns[1]
        return self.links[self.links[subj_name_key] == subj_name][subj_link_key].values[0]
