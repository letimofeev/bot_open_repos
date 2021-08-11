import logging
import os
from typing import NamedTuple

from dotenv import load_dotenv

from keyboard import VkKeyboard


logging.basicConfig(
    filename='debug.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
f_handler = logging.FileHandler(filename='errors.log', mode='w')
f_handler.setLevel(logging.WARNING)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class PostgresSQLSettings(NamedTuple):
    DB_NAME = os.environ.get("DB_NAME")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")


class GoogleAPISettings(NamedTuple):
    FILENAME = os.environ.get("GOOGLE_FILENAME")
    SCOPES = ['https://www.googleapis.com/auth/drive']
    API_NAME = "drive"
    API_VERSION = "v3"


class WolframalphaAPISettings(NamedTuple):
    TOKEN = os.environ.get("WOLFRAMALPHA_TOKEN")


class FileName(NamedTuple):
    LINKS = {
        "1 курс": "1 курс.csv",
        "2 курс": "2 курс.csv",
        "3 курс": "3 курс.csv",
        "4 курс": "4 курс.csv"
    }
    SCHEDULE = "Raspisanie_VESNA_2021.xlsx"
    GRAPH = "graph.jpg"
    FILTER = "filter.php"


class VKSettings(NamedTuple):
    ADMINS = [int(item) for item in os.environ.get("VK_ADMINS").split(',')]
    TOKEN = os.environ.get("VK_TOKEN")


class VKTableName(NamedTuple):
    REG_INFO = os.environ.get("DB_VK_REG_INFO")
    USERS = os.environ.get("DB_VK_USERS")
    MESSAGES = os.environ.get("DB_VK_MESSAGES")
    CUSTOM_ANSWERS = os.environ.get("DB_CUSTOM")
    COMMANDS = os.environ.get("DB_COMMANDS")
    PHOTO_LINKS = os.environ.get("DB_PHOTO")
    USER_STATUS = os.environ.get("DB_VK_USER_STATUS")
    BAN_LIST = os.environ.get("DB_VK_BAN")


class VKKeyboardName(NamedTuple):
    START = {
        "start1": "vk_start_keyboard.json",
        "start2": "vk_other_keyboard.json"
    }
    COURSES = "vk_courses_keyboard.json"
    GROUPS = {
        "1 курс": "vk_course1_keyboard.json",
        "2 курс": "vk_course2_keyboard.json",
        "3 курс": "vk_course3_keyboard.json",
        "4 курс": "vk_course4_keyboard.json"
    }
    LECTURES = {
        "1 курс": "vk_lectures_keyboard1.json",
        "2 курс": "vk_lectures_keyboard2.json",
        "3 курс": "vk_lectures_keyboard3.json",
        "4 курс": "vk_lectures_keyboard4.json"
    }
    DAYS = "vk_days_keyboard.json"
    VAR_NUM = "vk_dimensions.json"


class PlatformVK(NamedTuple):
    settings = VKSettings
    keyboard = VkKeyboard
    keyboard_name = VKKeyboardName
    table_name = VKTableName


class UserStatus(NamedTuple):
    ANY = "any"
    REG_COURSE = "reg_course"
    REG_GROUP = "reg_group"
    LINK = "link"
    SCHEDULE = "schedule"
    QUERY = "query"
    VAR_NUM = "graph_var_num"
    FUNC = "graph_func"
    CUSTOM_TO_ANSWER = "custom_text_to_answer"
    CUSTOM_ANSWER = "custom_answer"


class UserCallbackKey(NamedTuple):
    COURSE_NAME = "course_name"
    VAR_NUM = "var_num"
    CUSTOM_TO_ANSWER = "q"


class TextToAnswer(NamedTuple):
    CHANGE_REG_INFO = "изменить данные"
    GET_TEACHER_INGO = "who added "
    LECTURES = "лекции"
    SCHEDULE = "расписание"
    DELETE_CUSTOM = "delete "
    OTHER_MATERIALS = "остальные материалы"
    SECOND_MENU = "другое"
    RETURN_MAIN_MENU = "вернуться в главное меню"
    QUERY = "запрос"
    GRAPH = "график"
    BAN = "ban "
    TEACH = "обучить бота"


class AnswerKey(NamedTuple):
    KEYBOARD = "keyboard"
    TEXT_ANSWER = "answer"
    PHOTO_LINK = "photo_link"
    DEFAULT_KEYBOARD = "default_keyboard"
    PHOTO_FILE = "photo_file"


class AnswerValue(NamedTuple):
    # registration
    CHOOSE_COURSE_GREETING = "Приветствую! Для продолжения пройдите краткую регистрацию\nВыберите курс"
    CHOOSE_COURSE_CHANGING = "Для продолжения пройдите краткую регистрацию\nВыберите курс"
    CHOOSE_COURSE_TO_CONTINUE = "Для продолжения выберите курс"
    CHOOSE_GROUP = "Выберите группу"
    CHOOSE_GROUP_TO_CONTINUE = "Для продолжения выберите группу"
    REG_FINISH = 'Вы успешно прошли регистрацию. Для изменения данных введите "Изменить данные"'

    # get_teacher_info
    TEACHER_INFO = "Имя: {}\nФамилия: {}\nid: {}\nУстановленный ответ на сообщение: {}"
    ANSWER_NOT_SET = "Ответ на это сообщение не установлен"  # delete_answer

    # get_answer_links
    CHOOSE_SUBJECT = "Выберите предмет:"

    # get_answer_schedule
    CHOOSE_DAY = "Выберите день недели:"

    # delete_answer
    CUSTOM_DELETED = 'Ответ на сообщение "{}" удален'

    # other_materials
    OTHER_MATERIALS = "link"

    # switch_menu
    OTHER_FUNC = "Другие функции бота:"
    MAIN_MENU = "Главное меню:"

    # get_answer_query
    INPUT_QUERY = "Введите текст запроса (запрос нужно писать на английском)"
    QUERY_FAILED = "Я не смог обработать этот запрос"

    # get_answer_graph
    CHOOSE_VAR_NUM = "Выберите количество переменных:"
    INPUT_FUNC = "Введите функцию, график которой надо построить"
    WRONG_VAR_NUM = "Неверное количество переменных"
    GRAPH_FINISH = "График функции {}:"
    GRAPH_FAILED = "Я не смог построить этот график"

    # ban
    BANNED = "Пользователь забанен"

    # unban
    UNBANNED = "Пользователь разбанен"
    WAS_NOT_BANNED = "Пользователь не был забанен"

    # teach_bot
    CUSTOM_TO_ANSWER = "Напишите фразу, на которую бот будет отвечать: "
    CUSTOM_FILTER_REJECT = "Нельзя обучать бота мату"
    CUSTOM_RESERVED_REJECT = "Эта фраза зарезервирована"
    CUSTOM_TAUGHT_REJECT = "Этой фразе бот уже обучен"
    CUSTOM_ANSWER = "Напишите фразу, которой бот будет отвечать на введённую вами ранее"
    CUSTOM_FINISH = "Вы успешно обучили бота"

