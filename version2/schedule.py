from abc import ABCMeta, abstractmethod, ABC

from file_loader import PandasLoader
from settings import logger


class ISchedule(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_schedule_str(self, day: str) -> str:
        raise NotImplementedError


class PandasSchedule(ISchedule):
    def __init__(self, filename: str, course: str, group: str):
        self.schedule = PandasLoader().get_excel(filename, course)
        self.group_num = int(group[-1])
        self.day_case = {
            "понедельник": "понедельник",
            "вторник": "вторник",
            "среда": "среду",
            "четверг": "четверг",
            "пятница": "пятницу",
            "суббота": "субботу"}
        self.days = list(self.day_case.keys())

    def get_schedule_str(self, day: str) -> str:
        if self.schedule is None:
            return "Произошла ошибка на сервере, расписание недоступно"
        day_sch = f"Расписание на {self.day_case[day]}\n"
        max_pairs_in_day = 8
        for i in range(self.days.index(day) * max_pairs_in_day + 1, (self.days.index(day) + 1) * max_pairs_in_day):
            time = str(self.schedule[self.schedule.columns[1]].tolist()[i])
            cell_value = str(self.schedule[self.schedule.columns[self.group_num + 1]].tolist()[i]).split('\\')
            if len(cell_value) == 1 and cell_value[0] == "nan":
                day_sch += f"\n⌚{time}⌚\nНет пары\n"
            elif len(cell_value) != 5:
                logger.warning("get_schedule_str(): the number of fields is not correct, check schedule file")
                day_sch += f"\n⌚{time}⌚\nError\n"
            else:
                subj, pair_type, teacher, audi, form = cell_value
                day_sch += \
                    (f"\n⌚{time}⌚\n" +
                     f"{subj}\n" +
                     f"{pair_type}\n" +
                     f"Преподаватель: {teacher}\n" +
                     f"Аудитория: {audi}\n" +
                     f"Форма проведения: {form}\n")
        return day_sch
