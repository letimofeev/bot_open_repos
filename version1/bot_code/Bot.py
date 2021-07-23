import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from vk_api.utils import get_random_id
import distance
from Logs import *
import traceback
import datetime
from Commander import Answerer
from Configuration import Configuration as Cfg
from abc import ABCMeta, abstractmethod, ABC
import telebot as tb
import random
from Settings import *


class IBot(ABC):
    """
    Интерфейс класса бот
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user_course(self, peer_id):
        raise NotImplementedError

    @abstractmethod
    def get_user_group(self, peer_id):
        raise NotImplementedError

    @abstractmethod
    def get_user(self, event):
        raise NotImplementedError

    @abstractmethod
    def send_message(self, peer_id, mess, keyboard=None):
        raise NotImplementedError

    @abstractmethod
    def send_photo(self, peer_id, image_url=None, file_name=None):
        raise NotImplementedError

    @abstractmethod
    def answer(self, event):
        raise NotImplementedError

    @abstractmethod
    def not_found(self, peer_id, text):
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
    logs: dict
        Словарь с логами
    __admins: list
        Список id администраторов
    __last_messages: dict
        Словарь для сохранения последних полученных сообщений (хранит до 3 сообщений от пользователя)
    __used: bool
        Переменная для отслеживания произошел ли ответ пользователю

    """
    def __init__(self):
        try:
            self.vk = vk_api.VkApi(token=Constants.vk_token.value, captcha_handler=self.captcha_handler)
            self.long_poll = VkLongPoll(self.vk)
            self.vk_api = self.vk.get_api()
            self.upload = VkUpload(self.vk_api)
            self.session = requests.Session()
            self.__last_messages = {}
            self.__used = False
            self.logs = {'ban_logs': Logs('vk_banned'), 'error_logs': Logs('vk_errors'), 'users_logs': Logs('vk_users'),
                         'messages_logs': Logs('vk_messages'), 'users_groups': Logs('vk_users_data'),
                         'teach': Logs('vk_teach'), 'whitelist': Logs('vk_whitelist')}
            self.__admins = [170386588, 174445151]
        except Exception as e:
            time_ = str(datetime.datetime.now())
            error = pd.DataFrame.from_dict({
                'time:': [time_],
                'error_code:': [type(e).__name__],
                'traceback:': [traceback.format_exc()]})
            error.to_csv("errors_bot_init.csv")

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

    def get_user_course(self, peer_id: int) -> str:
        """
        Получение курса пользователя

        Функция получает по id курс в строковом формате из логов

        Parameters
        ----------
        peer_id: int
            id пользователя

        Returns
        -------
        str
            Курс пользователя
        """
        return self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == peer_id]['user_course'].values[0]

    def get_user_group(self, peer_id: int) -> str:
        """
        Получение группа пользователя

        Функция получает по id группу в строковом формате из логов

        Parameters
        ----------
        peer_id: int
            id пользователя

        Returns
        -------
        str
            Группа пользователя

        """
        return self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == peer_id]['user_group'].values[0]

    def get_user(self, event: vk_api.longpoll.Event) -> None:
        """
        Запись данных о пользователе в базу данных

        Функция обновляет объект класса Logs с помощью метода update

        Parameters
        ----------
        event: vk_api.longpoll.Event
            Объект vk сообщения

        Returns
        -------
        None
        """
        try:
            self.logs['users_logs'].update(
                event.peer_id,
                self.get_user_first_name(event),
                self.get_user_last_name(event),
                datetime.datetime.now()
            )
            self.logs['users_logs'].data = self.logs['users_logs'].data.drop_duplicates(['user_id', 'name', 'surname'])
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(event.peer_id, time_, type(e).__name__, str(e), traceback.format_exc())

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
        try:
            if keyboard is None:
                keyboard = Cfg.Keyboard.json_to_keyboard(Cfg.prefix + "start_keyboard.json")
            self.vk_api.messages.send(
                peer_id=peer_id,
                message=text,
                random_id=get_random_id(),
                # уникальный идентификатор, предназначенный для предотвращения повторной отправки одинакового сообщения
                keyboard=open(keyboard, "r", encoding="UTF-8").read()
            )
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

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
        try:
            if image_url is not None:
                image = self.session.get(image_url, stream=True)  # получение объекта по ссылке
                photo = self.upload.photo_messages(photos=image.raw)[0]  # необработанный запрос передается vk upload
                attachments = ['photo{}_{}'.format(photo['owner_id'], photo['id'])]  # медиавложение к личному сообщению
                self.vk_api.messages.send(
                    user_id=peer_id,
                    attachment=','.join(attachments),  # отправка вложений к сообщению
                    random_id=get_random_id()
                    # уникальный id, предназначенный для предотвращения повторной отправки одинакового сообщения
                )
            if file_name is not None:
                a = self.vk_api.photos.getMessagesUploadServer()
                b = requests.post(a['upload_url'], files={'photo': open(file_name, 'rb')}).json()
                c = self.vk_api.photos.saveMessagesPhoto(
                    photo=b['photo'],
                    server=b['server'],
                    hash=b['hash'])[0]
                d = "photo{}_{}".format(c["owner_id"], c["id"])
                self.vk_api.messages.send(user_id=peer_id, attachment=d, random_id=get_random_id())
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

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
        try:
            if self.__used:
                return
            if self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == event.peer_id]['user_course'].values:
                course, group = self.get_user_course(event.peer_id)[0], int(self.get_user_group(event.peer_id)[-1])
            else:
                course, group = None, None
            name = self.get_user_first_name(event)
            surname = self.get_user_last_name(event)
            answer = Answerer(answers=self.__last_messages).\
                get_answer(event.peer_id, event.text, name, surname, course, group, self.__admins, self.logs)
            if answer.get("answer"):
                if answer.get("last_messages") is not None:
                    self.__last_messages = answer.get("last_messages")
                if answer.get("photo_link") is not None:
                    self.send_photo(event.peer_id, answer.get("answer"))
                    self.__used = True
                    return
                if answer.get("photo_file") is not None:
                    self.send_message(event.peer_id, answer.get("answer"), answer.get("keyboard"))
                    self.send_photo(event.peer_id, file_name=answer.get("photo_file"))
                    self.__used = True
                    return
                self.send_message(event.peer_id, answer.get("answer"), answer.get("keyboard"))
                self.__used = True
        except Exception as e:
            time_ = str(datetime.datetime.now())
            print(traceback.format_exc())
            self.logs['error_logs'].update(event.peer_id, time_, type(e).__name__, str(e), traceback.format_exc())

    def not_found(self, peer_id: int, text: str) -> None:
        """
        Функция для случая когда пользователю не был отправлен ответ

        Если сообщение похоже на какое-то зарезервированное, то произойдет ответ на него,
        иначе пользователю отправляется сообщение "Шо?"

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
        try:
            text = text.lower()
            if not self.__used:
                if len(text) == 1:
                    self.send_message(peer_id, "Шо?")
                    return
                custom_file = Cfg.FileLoader(Cfg.Storage).get_csv(Cfg.prefix + "teach")
                for msg in list(Cfg.Messages(custom=custom_file).custom['Q']):
                    if distance.levenshtein(msg, text) <= Constants.levenshtein_dist.value:
                        self.__used = True
                        self.send_message(peer_id, Cfg.Messages(custom=custom_file).get_answer_custom(msg))
                        return
                photo_links_file = Cfg.FileLoader(Cfg.Storage).get_csv(file_name='photo_links')
                for msg in list(Cfg.Messages(photo_links=photo_links_file).photos):
                    if distance.levenshtein(msg, text) <= Constants.levenshtein_dist.value:
                        self.__used = True
                        self.send_photo(peer_id, Cfg.Messages(photo_links=photo_links_file).get_answer_photo(msg))
                        return
                if not self.__used:  # сообщение осталось необработанным
                    self.send_message(peer_id, "Шо?")
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())

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
        Cfg.Storage().download_folder_files(Cfg.prefix + "keyboards")
        for event in self.long_poll.listen():  # слушаем longpoll
            self.__used = False  # изначально ответ пользователю не произошёл
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:  # если пришло текстовое сообщение
                self.logs['messages_logs'].update(get_random_id(), event.peer_id, datetime.datetime.now(), event.text)
                self.get_user(event)  # собираем информацию о пользователе
                self.answer(event)
                self.not_found(event.peer_id, event.text)  # чтобы ответ пользователю в любом случае произошёл


class TgBot(IBot):
    """Класс TgBot используется для создания и запуска бота telegram

        Attributes
        ----------
        tg: tb.TeleBot
            Позволяет обращаться к методам API как к обычным классам
        logs: dict
            Словарь с логами
        __admins: list
            Список id администраторов
        __last_messages: dict
            Словарь для сохранения последних полученных сообщений (хранит до 3 сообщений от пользователя)
        __used: bool
            Переменная для отслеживания произошел ли ответ пользователю

        """
    def __init__(self):
        try:
            self.tg = tb.TeleBot(Constants.tg_token.value, parse_mode=None)
            self.__last_messages = {}
            self.logs = {'ban_logs': Logs('tg_banned'), 'error_logs': Logs('tg_errors'), 'users_logs': Logs('tg_users'),
                         'messages_logs': Logs('tg_messages'), 'users_groups': Logs('tg_users_data'),
                         'teach': Logs('tg_teach'), 'whitelist': Logs('tg_whitelist')}
            self.__admins = [900104261, 886302187]
            self.__used = False
        except Exception as e:
            time_ = str(datetime.datetime.now())
            error = pd.DataFrame.from_dict({
                'time:': [time_],
                'error_code:': [type(e).__name__],
                'traceback:': [traceback.format_exc()]})
            error.to_csv("errors_bot_init.csv")

    def send_message(self, peer_id: int, text: str, keyboard=None) -> None:
        """
        Отправка сообщения пользователю

        Функция использует метод класса Telebot send_message

        https://pypi.org/project/pyTelegramBotAPI/0.2.9/

        Parameters
        ----------
        peer_id: int
            id пользователя, которому нужно отправить сообщение
        text: str
            Сообщение, которое будет отправлено пользователю
        keyboard: Keyboard, default None
            Экранная клавиатура, которая будет показываться пользователю.
            Если keyboard None, то отправляется стартовая клавиатура

        Returns
        -------
        None
        """
        try:
            if keyboard is None:
                keyboard = Cfg.Keyboard.json_to_keyboard("tg_" + "start_keyboard.json")
            self.tg.send_message(peer_id, text, reply_markup=keyboard)
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

    def send_photo(self, peer_id: int, image_url: str = None, file_name: str = None) -> None:
        """
        Отправка изображения пользователю

        Функция использует метод класса Telebot send_photo

        https://pypi.org/project/pyTelegramBotAPI/0.2.9/

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
        try:
            if image_url is not None:
                self.tg.send_photo(peer_id, image_url)
            if file_name is not None:
                self.tg.send_photo(peer_id, photo=open(file_name, 'rb'))
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

    def get_user_first_name(self, event: tb.types.Message) -> str:
        """
        Получение имени пользователя

        Функция получает имя по id используя метод TgAPI from_user

        Parameters
        ----------
        event: tb.types.Message
            Объект vk сообщения

        Returns
        -------
        str
            Имя пользователя

        """
        return event.from_user.first_name

    def get_user_last_name(self, event: tb.types.Message) -> str:
        """
        Получение фамилии пользователя

        Функция получает фамилию по id используя метод TgAPI from_user

        Parameters
        ----------
        event: vk_api.longpoll.Event
            Объект vk сообщения

        Returns
        -------
        str
            Фамилия пользователя
        """
        return event.from_user.last_name

    def get_username(self, event: tb.types.Message) -> str:
        """
        Получение никнейма пользователя

        Функция получает фамилию по id используя метод TgAPI from_user

        Parameters
        ----------
        event: tb.types.Message
            объект сообщения
        Returns
        -------
        str
            Никнейм пользователя
        """
        return event.from_user.username

    def get_user_course(self, peer_id: int) -> str:
        """
        Получение курса пользователя

        Функция получает по id курс в строковом формате из логов

        Parameters
        ----------
        peer_id: int
            id пользователя

        Returns
        -------
        str
            Курс пользователя
        """
        return self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == peer_id]['user_course'].values[0]

    def get_user_group(self, peer_id: int) -> str:
        """
        Получение группа пользователя

        Функция получает по id группу в строковом формате из логов

        Parameters
        ----------
        peer_id: int
            id пользователя

        Returns
        -------
        str
            Группа пользователя

        """
        return self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == peer_id]['user_group'].values[0]

    def get_user(self, event: tb.types.Message) -> None:
        """
        Запись данных о пользователе в базу данных

        Функция обновляет объект класса Logs с помощью метода update

        Parameters
        ----------
        event: tb.types.Message
            Объект vk сообщения

        Returns
        -------
        None
        """
        try:
            self.logs['users_logs'].update(
                event.from_user.id,
                self.get_user_first_name(event),
                self.get_user_last_name(event),
                self.get_username(event),
                datetime.datetime.now()
            )
            self.logs['users_logs'].data = self.logs['users_logs'].data.drop_duplicates(['user_id', 'name', 'surname'])
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(event.from_user.id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

    def answer(self, event: tb.types.Message) -> None:
        """
        Функция, отправляющая ответ пользователю на его сообщение

        Если метод get_answer класса Answerer вернул ответ - отправка его методами send_photo / send_message.
        Если ответ произошел __used = True.

        Parameters
        ----------
        event: tb.types.Message
            Объект vk сообщения

        Returns
        -------
        None
        """
        try:
            self.logs['messages_logs'].update(random.randint(-1000000, 1000000), event.from_user.id, datetime.datetime.now(), event.text)
            self.get_user(event)
            self.__used = False
            if self.logs['users_groups'].data[self.logs['users_groups'].data['user_id'] == event.from_user.id]['user_course'].values:
                course, group = self.get_user_course(event.from_user.id)[0], int(self.get_user_group(event.from_user.id)[-1])
            else:
                course, group = None, None
            name = self.get_user_first_name(event)
            surname = self.get_user_last_name(event)
            answer = Answerer(answers=self.__last_messages). \
                get_answer(event.from_user.id, event.text, name, surname, course, group, self.__admins, self.logs)
            if answer.get("answer"):
                if answer.get("last_messages") is not None:
                    self.__last_messages = answer.get("last_messages")
                if answer.get("photo_link") is not None:
                    self.send_photo(event.from_user.id, answer.get("answer"))
                    self.__used = True
                    return
                if answer.get("photo_file") is not None:
                    self.send_message(event.from_user.id, answer.get("answer"), answer.get("keyboard"))
                    self.send_photo(event.from_user.id, file_name=answer.get("photo_file"))
                    self.__used = True
                    return
                self.send_message(event.from_user.id, answer.get("answer"), answer.get("keyboard"))
                self.__used = True
            self.not_found(event.from_user.id, event.text)
        except Exception as e:
            time_ = str(datetime.datetime.now())
            print(traceback.format_exc())
            self.logs['error_logs'].update(event.from_user.id, time_, type(e).__name__, str(e), traceback.format_exc())

    def not_found(self, peer_id: int, text: str) -> None:
        """
        Функция для случая когда пользователю не был отправлен ответ

        Если сообщение похоже на какое-то зарезервированное, то произойдет ответ на него,
        иначе пользователю отправляется сообщение "Шо?"

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
        try:
            text = text.lower()
            if not self.__used:
                if len(text) == 1:
                    self.send_message(peer_id, "Шо?")
                    return
                custom_file = Cfg.FileLoader(Cfg.Storage).get_csv(Cfg.prefix + "teach")
                for msg in list(Cfg.Messages(custom=custom_file).custom['Q']):
                    if distance.levenshtein(msg, text) <= Constants.levenshtein_dist.value:
                        self.__used = True
                        self.send_message(peer_id, Cfg.Messages(custom=custom_file).get_answer_custom(msg))
                        return
                photo_links_file = Cfg.FileLoader(Cfg.Storage).get_csv(file_name='photo_links')
                for msg in list(Cfg.Messages(photo_links=photo_links_file).photos):
                    if distance.levenshtein(msg, text) <= Constants.levenshtein_dist.value:
                        self.__used = True
                        self.send_photo(peer_id, Cfg.Messages(photo_links=photo_links_file).get_answer_photo(msg))
                        return
                if not self.__used:  # сообщение осталось необработанным
                    self.send_message(peer_id, "Шо?")
        except Exception as e:
            time_ = str(datetime.datetime.now())
            self.logs['error_logs'].update(peer_id, time_, type(e).__name__, str(e), traceback.format_exc())
            print(traceback.format_exc())

    def start(self) -> None:
        """
        Функция, запускающая работу бота

        Используется метод класса Telebot polling

        Returns
        -------
        None
        """
        Cfg.Storage().download_folder_files(Cfg.prefix + "keyboards")
        mess_dict = dict(
            function=lambda msg, obj=self: obj.answer(msg),
            filters=dict(
                content_types=['text'],
            )
        )
        self.tg.add_message_handler(mess_dict)
        self.tg.polling()
