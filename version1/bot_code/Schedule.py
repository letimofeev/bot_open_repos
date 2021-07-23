from Settings import Constants
from abc import ABCMeta, abstractmethod


class ISchedule:
    """
    Интерфейс класса с расписанием
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_schedule_str(self, course: str, group_num: int, day: str) -> str:
        raise NotImplementedError


class PandasSchedule(ISchedule):
    """Класс для получения расписания

    Attributes
    ----------
    sch: pd.ExcelFile
        Excel файл с расписанием
    Messages: Messages
        Класс Messages для получения зарезервированных фраз
    """
    def __init__(self, Messages, schedule):
        self.sch = schedule
        self.Messages = Messages

    def get_schedule_str(self, course: str, group_num: int, day: str) -> str:
        """
        Получение расписания заданной группы

        Parameters
        ----------
        course: str
            Курс в строковом формате (пр. "2 курс")
        group_num: int
            Номер группы (пр. 5)
        day: str
            День недели

        Returns
        -------
        str
            Строка с расписанием
        """
        days = self.Messages().get_days()
        df = self.sch.parse(course)
        df = df.fillna('')
        day_sch = ""
        n = Constants.max_pairs_per_day.value
        cycle_range = (days.index(day) * n, (days.index(day) + 1) * n)
        for i in range(cycle_range[0], cycle_range[1]):
            time = str(list(df[df.columns[1]])[i])
            subj = str(list(df[df.columns[group_num + 1]])[i])
            day_sch += ("{0:12}{1:10}\n".format(time, subj))
        return day_sch

