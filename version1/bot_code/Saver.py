from Storage import GoogleAPI
from FileLoader import PandasLoader
import datetime
import time


class PandasSaver:
    """
    Класс для выгрузки логов на Storage

    Attributes
    ----------
    FileLoader: FileLoader, default PandasLoader
        Класс для доступа к файлам и их обновления
    """
    def __init__(self, FileLoader=PandasLoader):
        self.FileLoader = FileLoader

    def upload_files(self, logs: dict, now: bool = False) -> None:
        """
        Выгрузка логов на диск

        Parameters
        ----------
        logs: dict
            Словарь с объектами класса Logs, хранящий данные, которые нужно выгрузить
        now: bool, default False
            Если True - выгрузить логи сейчас, иначе логи выгружаются раз в час

        Returns
        -------
        None
        """
        if now:
            for i, log in logs.items():
                self.FileLoader().update_csv(log.name, log.data)
                print(f"файл {log.name}.csv успешно выгружен на гугл диск {datetime.datetime.now()}")
            return
        while True:
            time.sleep(0.5)
            if datetime.datetime.now().second == 0 and datetime.datetime.now().minute == 0:
                for i, log in logs.items():
                    self.FileLoader().update_csv(log.name, log.data)
                    print(f"файл {log.name}.csv успешно выгружен на гугл диск {datetime.datetime.now()}")

