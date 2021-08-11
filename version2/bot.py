import requests
from abc import ABCMeta, abstractmethod, ABC

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from vk_api.utils import get_random_id

from keyboard import VkKeyboard
from answer import Answerer
from user import SQLUser
from messages import SQLMessages
from settings import PlatformVK, logger, AnswerKey


class IBot(ABC):
    """
    Интерфейс класса бот
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_message(self, peer_id, mess, keyboard=None):
        raise NotImplementedError

    @abstractmethod
    def send_photo(self, peer_id, image_url=None, file_name=None):
        raise NotImplementedError

    @abstractmethod
    def message_handler(self, event):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError


class VkBot(IBot):
    """Класс VkBot используется для создания и запуска бота vk

    Attributes
    ----------
    vk: vk_api.VkApi
        Авторизация вк
    long_poll: VkLongPoll
        Вызываем longpoll для получения данных о новых событиях
    vk_api: vk.get_api
        Позволяет обращаться к методам API как к обычным классам
    upload: VkUpload
        Модуль для загрузки медиафайлов вк
    used: bool
        Переменная для отслеживания произошел ли ответ пользователю

    """
    def __init__(self, config):
        try:
            self.vk = vk_api.VkApi(token=PlatformVK.settings.TOKEN, captcha_handler=self.captcha_handler)
            self.long_poll = VkLongPoll(self.vk)
            self.vk_api = self.vk.get_api()
            self.upload = VkUpload(self.vk_api)
            self.session = requests.Session()
            self.default_keyboard = VkKeyboard.json_to_keyboard(PlatformVK.keyboard_name.START["start1"])
            self.answer_config = config
            self.used = False
        except Exception:
            logger.error("VkBot initialization failed", exc_info=True)
            raise

    @staticmethod
    def captcha_handler(captcha):
        """ При возникновении капчи вызывается эта функция и ей передается объект
            капчи. Через метод get_url можно получить ссылку на изображение.
            Через метод try_again можно попытаться отправить запрос с кодом капчи
        """

        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

        # Пробуем снова отправить запрос с капчей
        return captcha.try_again(key)

    def get_user_first_name(self, event: vk_api.longpoll.Event) -> str:
        """
        Получение имени пользователя

        Функция получает имя по id используя метод VkAPI users.get

        https://vk.com/dev/users.get

        Parameters
        ----------
        event: vk_api.longpoll.Event
            Объект vk сообщения

        Returns
        -------
        str
            Имя пользователя

        """
        return self.vk_api.users.get(user_id=event.peer_id)[0]['first_name']

    def get_user_last_name(self, event: vk_api.longpoll.Event) -> str:
        """
        Получение фамилии пользователя

        Функция получает фамилию по id используя метод VkAPI users.get

        https://vk.com/dev/users.get

        Parameters
        ----------
        event: vk_api.longpoll.Event
            Объект vk сообщения

        Returns
        -------
        str
            Фамилия пользователя
        """
        return self.vk_api.users.get(user_id=event.peer_id)[0]['last_name']

    def send_message(self, peer_id: int, text: str, keyboard=None) -> None:
        """
        Отправка сообщения пользователю

        Функция использует метод VkAPI messages.send

        https://vk.com/dev/messages.send

        Parameters
        ----------
        peer_id: int
            id пользователя, которому нужно отправить сообщение
        text: str
            Сообщение, которое будет отправлено пользователю
        keyboard: Keyboard, default None
            Экранная клавиатура, которая будет показываться пользователю.
            Если keyboard = None, то отправляется стартовая клавиатура

        Returns
        -------
        None
        """
        if keyboard is None:
            keyboard = self.default_keyboard
        self.vk_api.messages.send(
            peer_id=peer_id,
            message=text,
            random_id=get_random_id(),
            # уникальный идентификатор, предназначенный для предотвращения повторной отправки одинакового сообщения
            keyboard=open(keyboard, "r", encoding="UTF-8").read()
        )

    def send_photo(self, peer_id: int, image_url: str = None, file_name: str = None):
        """
        Отправка изображения пользователю

        Функция использует метод VkAPI messages.send

        https://vk.com/dev/messages.send

        Если image_url не None - отправка изображения по ссылке,
        если file_name не None - отправка изображения по названию файла

        Parameters
        ----------
        peer_id: int
            id пользователя, которому нужно отправить изображение
        image_url: str
            Ссылка на изображение
        file_name: str, default None
            Название файла с изображением

        Returns
        -------
        None

        Note:
            Если image_url и file_name одновременно не None, то отправится изображение по ссылке
        """
        if image_url is not None:
            image = self.session.get(image_url, stream=True)  # получение объекта по ссылке
            photo = self.upload.photo_messages(photos=image.raw)[0]  # необработанный запрос передается vk upload
            attachments = [f"photo{photo['owner_id']}_{photo['id']}"]  # медиавложение к личному сообщению
            self.vk_api.messages.send(
                user_id=peer_id,
                attachment=','.join(attachments),  # отправка вложений к сообщению
                random_id=get_random_id()
                # уникальный id, предназначенный для предотвращения повторной отправки одинакового сообщения
            )
        if file_name is not None:
            server = self.vk_api.photos.getMessagesUploadServer()
            post = requests.post(server["upload_url"], files={"photo": open(file_name, "rb")}).json()
            photo = self.vk_api.photos.saveMessagesPhoto(
                photo=post["photo"],
                server=post["server"],
                hash=post["hash"])[0]
            attachments = [f"photo{photo['owner_id']}_{photo['id']}"]
            self.vk_api.messages.send(
                user_id=peer_id,
                attachment=','.join(attachments),
                random_id=get_random_id())

    def answer(self, event: vk_api.longpoll.Event) -> None:
        """
        Функция, отправляющая ответ пользователю на его сообщение

        Если метод get_answer класса Answerer вернул ответ - отправка его методами send_photo / send_message.
        Если ответ произошел __used = True.

        Parameters
        ----------
        event: vk_api.longpoll.Event
            Объект vk сообщения

        Returns
        -------
        None
        """
        answer = Answerer(
            answer_config=self.answer_config,
            platform_config=PlatformVK
        ).get_answer(peer_id=event.peer_id, text=event.text)

        if answer.get(AnswerKey.PHOTO_LINK):
            self.send_photo(
                peer_id=event.peer_id,
                image_url=answer.get(AnswerKey.PHOTO_LINK)
            )
            self.used = True

        if answer.get(AnswerKey.PHOTO_FILE):
            self.send_photo(
                peer_id=event.peer_id,
                file_name=answer.get(AnswerKey.PHOTO_FILE)
            )
            self.used = True

        if answer.get(AnswerKey.DEFAULT_KEYBOARD):
            self.default_keyboard = answer.get(AnswerKey.DEFAULT_KEYBOARD)

        if answer.get(AnswerKey.TEXT_ANSWER):
            self.send_message(
                peer_id=event.peer_id,
                text=answer.get(AnswerKey.TEXT_ANSWER),
                keyboard=answer.get(AnswerKey.KEYBOARD)
            )
            self.used = True

    def not_found(self, peer_id: int) -> None:
        """
        Функция для случая когда пользователю не был отправлен ответ
        Если used = False пользователю отправляется сообщение "Шо?"

        Parameters
        ----------
        peer_id: int
            id пользователя, от которого получено сообщение
        text: str
            Текст полученного сообщения
        Returns
        -------
        None
        """
        if not self.used:
            self.send_message(peer_id, "Шо?")

    def message_handler(self, event):
        try:
            SQLUser(PlatformVK.table_name).log_user(
                user_id=event.peer_id,
                name=self.get_user_first_name(event),
                surname=self.get_user_last_name(event))
            SQLMessages(PlatformVK.table_name).log_message(
                message_id=event.message_id,
                user_id=event.peer_id,
                text=event.text)
            self.answer(event)
            self.not_found(event.peer_id)  # чтобы ответ пользователю в любом случае произошёл
        except Exception:
            logger.error("message_handler(): Exception occurred", exc_info=True)
            raise

    def start(self) -> None:
        """
        Функция, запускающая работу бота.

        При запуске скачиваются клавиатуры.
        Далее функция слушает longpoll, когда приходит текстовое сообщение, происходит логирование и вызов методов
        answer и not_found.

        Returns
        -------
        None
        """
        for event in self.long_poll.listen():  # слушаем longpoll
            self.used = False  # изначально ответ пользователю не произошёл
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:  # если пришло текстовое сообщение
                self.message_handler(event)

