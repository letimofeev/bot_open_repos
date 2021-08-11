import pandas as pd

from file_storage import GoogleAPI


class PandasLoader:
    """Класс для возвращения содержимого файлов в качестве Pandas объектов

    Attributes
    ----------
    Storage: storage, GoogleAPI default
        Место хранения файлов
    """
    def __init__(self):
        self.Storage = GoogleAPI

    @staticmethod
    def is_exist(file_name: str) -> bool:
        """
        Метод для проверки существования файла локально

        Parameters
        ----------
        file_name: str
            Имя файла

        Returns
        -------
        bool
            True, если файл уже существует, False иначе
        """
        try:
            with open(file_name):
                return True
        except FileNotFoundError:
            return False

    def get_csv(self, file_name: str, folder_name: str = None) -> pd.DataFrame:
        """
        Получение содержимого csv файла как Pandas таблички.

        Если folder_name не None - произойдет загрузка из Storage файлов из папки с названием folder_name.

        Parameters
        ----------
        file_name: str
            Название csv файла, содержимое которого нужно получить. Название можно писать без .csv
        folder_name: str, default None
            Название папки в Storage, из которой нужно получить файлы

        Returns
        -------
        pd.DataFrame
            Pandas таблица с содержимым файла
        """
        if file_name[-4:] != ".csv":
            file_name = f"{file_name}.csv"
        if self.is_exist(file_name):
            return pd.read_csv(file_name)
        if folder_name is not None:
            self.Storage().download_folder_files(folder_name)
        else:
            self.Storage().download_file(file_name)
        return pd.read_csv(file_name)

    def update_csv(self, file_name: str, df: pd.DataFrame) -> None:
        """
        Обновление содержимого file_name данными из Pandas таблицы df

        Parameters
        ----------
        file_name: str
            Название файла, содержимое которого нужно обновить
        df: pd.DataFrame

        Returns
        -------
        None
        """
        file_name = f"{file_name}.csv"
        df.to_csv(file_name, index=False)
        self.Storage().update_file(file_name, 'text/csv')

    def get_excel(self, file_name: str, sheet_name: str = None, folder_name: str = None) -> pd.ExcelFile or pd.DataFrame:
        """
        Получение содержимого excel файла как Pandas объекта.

        Если folder_name не None - произойдет загрузка из Storage файлов из папки с названием folder_name.

        Parameters
        ----------
        file_name: str
            Название excel файла, содержимое которого нужно получить. Название можно писать без .xlsx
        folder_name: str, default None
            Название папки в Storage, из которой нужно получить файлы
        sheet_name: str, default None
            Название страицы excel файла, которую надо считать

        Returns
        -------
        pd.ExcelFile или pd.DataFrame
            Pandas Excel file или Pandas таблица с содержимым страницы excel файла
        """
        if file_name[-5:] != ".xlsx":
            file_name = f"{file_name}.xlsx"
        if self.is_exist(file_name):
            if sheet_name is not None:
                return pd.ExcelFile(file_name).parse(sheet_name)
            else:
                return pd.ExcelFile(file_name)
        if folder_name is not None:
            self.Storage().download_folder_files(folder_name)
        else:
            self.Storage().download_file(file_name)
        if sheet_name is not None:
            return pd.ExcelFile(file_name).parse(sheet_name)
        return pd.ExcelFile(file_name)
