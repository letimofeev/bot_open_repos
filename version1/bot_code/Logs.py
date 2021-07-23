from typing import Any
import pandas as pd
from FileLoader import PandasLoader


class Logs:
    """
    Класс для хранения логов

    Attributes
    ----------
    name: str
        Название таблицы логов
    data: pandas.core.frame.DataFrame
        Pandas таблица логов
    """
    def __init__(self, name):
        self.name = name
        self.data = PandasLoader().get_csv(file_name=name)

    def update(self, *args: Any, change_row: bool = False) -> None:
        """
        Метод для добавления строки вниз DataFrame, значения элементов для всех столбцов берутся из args

        Parameters
        ----------
        change_row: bool, default False
            Булева переменная, если True, то update() обновляет строку, если False, то добавляет новую
        args: tuple or list
            Строка, которую надо добавить в датафрейм или изменить на эту строку уже существующую

        Returns
        -------
        None
        """
        if not change_row:
            self.data.index = [i for i in range(len(self.data.index))]
            self.data.loc[len(self.data.index), self.data.columns] = args
        else:
            self.data.loc[self.data[self.data[self.data.columns[0]]].index[0], self.data.columns] = args

    def get_rows(self, n: int = 1, all_: bool = False, columns: list = None, rows: list = None):
        """
        Метод для вывода в консоль: всей таблицы data, если all == True; столбиков с именами columns, если
        columns != None; строк с индексами rows, если rows != None; rows_number последних строчек, если all == False,
        columns == None и rows == None

        Parameters
        ----------
        n: int, default 1
            Количество строк снизу
        all_: bool, default None
            True или False в зависимости от желания
        columns: list, default None
            Список из названий колонок
        rows: list, default None
            Список из индексов строк

        Returns
        -------
        None
        """
        if all_:
            print(self.data)
        elif columns is not None:
            print(self.data[columns])
        elif rows is not None:
            print(self.data.loc[rows])
        else:
            print(self.data.tail(n))

    def clear(self, indexes=None, conditions=None):
        """
        Метод для очистки DataFrame

        Parameters
        ----------
        conditions: dict, default None
            Словарь условий по которым надо удалить строку: ключ - название столбца, value - значение этого столбца
        indexes: list, default None
            Список индексов строк, которые надо удалить

        Returns
        -------
        None
        """
        if indexes is None and conditions is None:
            self.data = pd.DataFrame(columns=self.data.columns)
        elif indexes is not None:
            self.data = self.data.drop(indexes, axis='index')
        else:
            rab = self.data
            for i, j in conditions.items():
                rab = rab.loc[rab[i] == j]
            self.data = self.data.drop(rab.index, axis='index')

