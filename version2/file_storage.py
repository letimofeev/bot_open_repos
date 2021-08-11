import io

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
from httplib2 import ServerNotFoundError
from abc import ABCMeta, abstractmethod, ABC

from settings import GoogleAPISettings, logger


class IStorage(ABC):
    """
    Интерфейс для класса хранилище
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_connection(self):
        raise NotImplementedError

    @abstractmethod
    def download_folder_files(self, folder_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_file(self, file_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_file(self, file_name: str, mime_type: str) -> None:
        raise NotImplementedError


class GoogleAPI(IStorage):
    """Класс для взаимодействия с файлами на Google диске

    Attributes
    ----------
    scopes: list:
        Права доступа
    api_name: str
        Название API сервиса
    api_version: str
        Версия API
    service: googleapiclient.discovery.Resource
        Подключение к диску
    files: dict
        Словарь с информацией о файлах, к которым имеется доступ

    """
    def __init__(self):
        self.key_file_name = GoogleAPISettings.FILENAME
        self.scopes = GoogleAPISettings.SCOPES
        self.api_name = GoogleAPISettings.API_NAME
        self.api_version = GoogleAPISettings.API_VERSION
        self.service = self.get_connection()
        self.files = self.get_files()

    def get_connection(self):
        """
        Подключение к GoogleAPI

        Returns
        -------
        googleapiclient.discovery.Resource()
            Объект сервиса

        Raises
        ------
        GDConnection
            Если соединение с Google не будет установлено
        """
        service = None
        try:
            credentials = service_account.Credentials.from_service_account_file(self.key_file_name, scopes=self.scopes)
            service = build(self.api_name, self.api_version, credentials=credentials)
            logger.debug("Connection to GoogleDisk successful")
        except ServerNotFoundError:
            logger.error("Connection to GoogleDisk failed", exc_info=True)
        finally:
            return service

    def get_files(self) -> dict:
        """
        Получение словаря файлов, к которым имеется доступ

        Returns
        -------
        dict
            Словарь с информацией о файлах
        """
        results = self.service.files().list(pageSize=10,
                                            fields="nextPageToken, files(id, name, mimeType)").execute()
        nextPageToken = results.get('nextPageToken')
        while nextPageToken:
            nextPage = self.service.files().list(
                pageSize=10,
                fields="nextPageToken, files(id, name, mimeType, parents)",
                pageToken=nextPageToken).execute()
            nextPageToken = nextPage.get('nextPageToken')
            results['files'] = results['files'] + nextPage['files']
        logger.debug("get_files(): status message: %s", "OK")
        return results

    def get_id(self, file_name: str) -> int:
        """
        Получение id объекта на Google диске

        Parameters
        ----------
        file_name: str
            Название объекта, id которого надо получить

        Returns
        -------
        int
            id объекта

        Raises
        ------
        NameError
            Если объекта с указанным названием нет на диске
        """
        object_id = None
        for i in range(len(self.files.get('files'))):
            if self.files.get('files')[i]['name'] == file_name:
                object_id = self.files.get('files')[i]['id']
        if object_id is None:
            raise NameError(f"Object with name {file_name} doesn't exist")
        return object_id

    def get_folder_files_list(self, folder_name: str) -> list:
        """
        Получение списка с содержимым папки

        Parameters
        ----------
        folder_name: str
            Название папки

        Returns
        -------
        list
            Данные файлов из папки
        """
        folder_id = self.get_id(folder_name)
        folder_files = self.service.files().list(
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, parents, createdTime)",
            q=f"'{folder_id}' in parents").execute()
        return folder_files['files']

    def download_folder_files(self, folder_name: str) -> bool:
        """
        Скачивание файлов из папки

        Parameters
        ----------
        folder_name:
            Название папки, из которой надо скачать файлы

        Returns
        -------
        bool
            Статус загрузки, True если не произошло ошибок
        """
        files_ids = []
        files_names = []
        files_dict = self.get_folder_files_list(folder_name)
        for i in range(len(files_dict)):
            files_ids.append(files_dict[i]['id'])
            files_names.append(files_dict[i]['name'])
            request = self.service.files().get_media(fileId=files_ids[i])
            fh = io.FileIO(files_names[i], 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                done = downloader.next_chunk()
        logger.debug("download_folder_files(): status message: %s", "OK")
        return True

    def download_file(self, file_name: str) -> bool:
        """
        Скачивание файла с Google диска

        Parameters
        ----------
        file_name: название файла, который нужно загрузить

        Returns
        -------
        bool
            Статус загрузки, True если не произошло ошибок
        """
        file_id = self.get_id(file_name)
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            done = downloader.next_chunk()
        logger.debug("download_file(): status message: %s", "OK")
        return True

    def update_file(self, file_name: str, mime_type: str) -> bool:
        """
        Обновление содержимого существующего на диске файла

        Parameters
        ----------
        file_name: str
            Имя файла
        mime_type: str
            Тип файла

        Returns
        -------
        None
        """
        file_id = self.get_id(file_name)
        file_metadata = {'name': file_name}
        media = MediaFileUpload(filename=file_name,
                                mimetype=mime_type)
        self.service.files().update(fileId=file_id,
                                    body=file_metadata,
                                    media_body=media).execute()
        logger.debug("update_file(): status message: %s", "OK")
        return True
