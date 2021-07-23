from Ban import *
from Interpreter import *
from Configuration import Configuration
from Filter import BadWordsFilter
import datetime


class Answerer:
    """Класс для получения ответа на полученное сообщение

    Attributes
    ----------
    FileLoader
        Класс для доступа к файлам и их обновления
    Links
        Класс для получения ссылок на занятия из файла
    Schedule
        Класс для получения расписания
    Messages
        Класс для хранения и получения зарезервированных ответов и сообщений
    Storage
        Класс для взаимодействия с файлами в хранилище
    QueryResponder
        Класс для ответа на запросы
    GraphBuilder
        Класс для построения графиков
    Keyboard
        Класс клавиатуры
    Saver
        Класс для логирования
    prefix: str
        Префикс для названия файлов клавиатур и логов
    __answers: dict, default None
        Словарь последних сообщений для запоминания предыдущих ответов
    """
    def __init__(self, answers=None):
        if answers is None:
            answers = {}
        self.__answers = answers
        self.FileLoader = Configuration.FileLoader
        self.Links = Configuration.Links
        self.Schedule = Configuration.Schedule
        self.Messages = Configuration.Messages
        self.Storage = Configuration.Storage
        self.QueryResponder = Configuration.QueryResponder
        self.GraphBuilder = Configuration.GraphBuilder
        self.Keyboard = Configuration.Keyboard
        self.prefix = Configuration.prefix
        self.Saver = Configuration.Saver

    def get_teacher_info(self, peer_id: int, text: str, name: str, surname: str, admins: list) -> dict:
        """
        Получение информации о пользователе, обучившего бота

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        name: str
            Имя пользователя
        surname: str
            Фамилия пользователя
        admins: list
            Список id администраторов

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        prefix_size = len("who added ")
        if text[:prefix_size] == "who added " and peer_id in admins:
            phrase = text[prefix_size:]
            custom_file = self.FileLoader(self.Storage).get_csv(self.prefix+"teach")
            if phrase in list(self.Messages(custom=custom_file).custom['Q']):
                customer_id = int(self.Messages(custom=custom_file).get_teacher_id(phrase))
                answer = self.Messages(custom=custom_file).get_answer_custom(phrase)
                if surname is None:
                    surname = "None"
                return {"answer": ('Имя: ' + name + '\n' +
                                   'Фамилия: ' + surname + '\n' +
                                   'id: ' + str(customer_id) + '\n' +
                                   "Установленный ответ на сообщение: " + answer)}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_command(self, peer_id: int, text: str) -> dict:
        """
        Получение ответа на команду

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя, не используется в функции, но нужен для проверки наличия бана у пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        commands_file = self.FileLoader(self.Storage).get_csv(file_name='commands')
        if text in list(self.Messages(commands=commands_file).commands):
            return {"answer": self.Messages(commands=commands_file).get_answer_command(text)}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_links(self, peer_id: int, text: str, course: str) -> dict:
        """
        Получение ссылки на занятие

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        course: str
            Номер курса

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "last_messages" хранится словарь сохраненных сообщений

            По ключу "keyboard" хранится клавиатура для сообщения
        """
        text = text.lower()
        if course is None:
            return {"answer": False}
        if text == 'лекции':
            self.__answers.update({peer_id: [text]})
            return {"last_messages": self.__answers,
                    "answer": 'Выберите предмет:',
                    "keyboard": self.Keyboard.json_to_keyboard(self.prefix+f"lectures_keyboard{course}.json")}
        links_file = self.FileLoader(self.Storage).get_csv(file_name=f'{course} курс', folder_name='Ссылки на занятия')
        if text in self.Links(links_file).get_subj_list() and self.__answers.get(peer_id) is not None:
            if len(self.__answers[peer_id]):
                if self.__answers[peer_id][0] == 'лекции':
                    self.__answers[peer_id].clear()
                    return {"last_messages": self.__answers, "answer": self.Links(links_file).get_subj_link(text)}
        return {"last_messages": self.__answers, "answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_schedule(self, peer_id: int, text: str, course: str, group: int) -> dict:
        """
        Получение расписания

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        course: str
            Номер курса
        group: int
            Номер группы

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "last_messages" хранится словарь сохраненных сообщений

            По ключу "keyboard" хранится клавиатура для сообщения
        """
        text = text.lower()
        if course is None or group is None:
            return {"answer": False}
        if text == 'расписание':
            self.__answers.update({peer_id: [text]})
            return {"last_messages": self.__answers,
                    "answer": 'Выберите день недели:',
                    "keyboard": self.Keyboard.json_to_keyboard(self.prefix+"days_keyboard.json")}
        schedule_file = self.FileLoader(self.Storage).get_excel(file_name='Raspisanie_VESNA_2021')
        if text in self.Messages().get_days() and self.__answers.get(peer_id) is not None:
            if len(self.__answers[peer_id]):
                if self.__answers[peer_id][0] == 'расписание':
                    self.__answers[peer_id].clear()
                    return {"last_messages": self.__answers,
                            "answer": self.Schedule(self.Messages, schedule_file).get_schedule_str(f'{course} курс', group, text)}
        return {"last_messages": self.__answers, "answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_text(self, peer_id: int, text: str) -> dict:
        """
        Получение ответа на текстовое сообщение

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя, не используется в функции, но нужен для проверки наличия бана у пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        custom_file = self.FileLoader(self.Storage).get_csv(self.prefix+"teach")
        if text in list(self.Messages(custom=custom_file).custom['Q']):
            return {"answer": self.Messages(custom=custom_file).get_answer_custom(text)}
        return {"answer": False}

    def delete_answer_text(self, peer_id: int, text: str, admins: list, logs: dict) -> dict:
        """
        Удаление установленного пользователем ответа на сообщение

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        prefix_size = len("delete ")
        if text[:prefix_size] == "delete " and peer_id in admins:
            phrase = text[prefix_size:]
            custom_file = self.FileLoader(self.Storage).get_csv(self.prefix+"teach")
            if phrase in list(self.Messages(custom=custom_file).custom['Q']):
                logs['teach'].clear(conditions={'Q': phrase})
                self.FileLoader().update_csv(self.prefix+"teach", logs["teach"].data)
                return {"answer": f'Ответ на сообщение "{phrase}" удален'}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_photo(self, peer_id: int, text: str) -> dict:
        """
        Получение изображения в ответ на текстовое сообщение

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя, не используется в функции, но нужен для проверки наличия бана у пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "photo_link" хранится bool переменная, если True - в "answer" ссылка на изображение
        """
        text = text.lower()
        photo_links_file = self.FileLoader(self.Storage).get_csv(file_name='photo_links')
        if text in list(self.Messages(photo_links=photo_links_file).photos):
            return {"answer": self.Messages(photo_links=photo_links_file).get_answer_photo(text), "photo_link": True}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_query(self, peer_id: int, text: str) -> dict:
        """
        Получение ответа на запрос

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя, не используется в функции, но нужен для проверки наличия бана у пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        prefix_size = len("запрос ")
        if text[:prefix_size] == "запрос ":
            query_text = text[prefix_size:]
            answer = self.QueryResponder().query(query_text)
            if answer:
                return {"answer": answer}
            else:
                return {"answer": "Я не смог обработать твой вопрос, задай другой"}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def get_answer_graph(self, peer_id: int, text: str) -> dict:
        """
        Получение графика функции

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя, не используется в функции, но нужен для проверки наличия бана у пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "photo_file" хранится название jpg файла с графиком
        """
        try:
            text = text.lower()
            prefix_size = len("график ")
            if text[:prefix_size] == "график ":
                dimension = text[prefix_size]
                if not (dimension == '2' or dimension == '3'):
                    return {"answer": "Неверная размерность"}
                func = text[10:]
                self.GraphBuilder().save_plot(func, int(dimension), 'graph')
                return {"answer": f"График функции {func}", "photo_file": "graph.jpg"}
            return {"answer": False}
        except KeyError:
            return {"answer": "Я не смог построить этот график, попробуй другой"}

    @AccessLimiter.whitelist_check(Configuration)
    def get_answer_code(self, peer_id: int, text: str) -> dict:
        """
        Получение результата выполнения кода

        Функция доступна только пользователям в whitelist'е

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        prefix_size = len("code ")
        if text[:prefix_size] == "code ":
            language = text[prefix_size:]
            if not (language == 'php' or language == 'python'):
                return {"answer": "Выполнять программы на этом языке я не умею"}
            text = "code"
            self.__answers.update({peer_id: [text]})
            self.__answers[peer_id].append(language)
            return {"answer": f"Введите код на {language} (для питона отступы пишите через \\t)",
                    "last_messages": self.__answers}

        elif self.__answers.get(peer_id) is not None:
            if len(self.__answers[peer_id]) == 2 and self.__answers[peer_id][0] == "code":
                self.__answers[peer_id].append(text)
                return {"answer": "Введите аргументы для программы через пробел (если аргументов нет введите no args",
                        "last_messages": self.__answers}

            if len(self.__answers[peer_id]) == 3 and self.__answers[peer_id][0] == "code":
                self.__answers[peer_id].append(text)
                if text == 'no args':
                    args = ''
                else:
                    args = self.__answers[peer_id][3]
                language, code = self.__answers[peer_id][1], self.__answers[peer_id][2]
                if language == 'php':
                    prefix, type_ = '<?php\n', '.php'
                else:
                    language = Configuration.python_version
                    prefix, type_ = 'import sys\n', '.py'
                executor = Interpreter(language, type_, prefix)
                result = executor.execute_code(code, args)
                self.__answers[peer_id].clear()
                if not result:
                    return {"answer": "Программа вернула пустую строку"}
                else:
                    return {"answer": result, "last_messages": self.__answers}
        return {"answer": False}

    def add_to_whitelist(self, peer_id: int, text: str, admins: list, logs: dict) -> dict:
        """
        Добавления пользователя в whitelist

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        prefix_size = len("whitelist add ")
        if text[:prefix_size] == "whitelist add " and peer_id in admins:
            user_id = int(text[prefix_size:])
            logs["whitelist"].update(user_id)
            self.FileLoader().update_csv(self.prefix+"whitelist", logs["whitelist"].data)
            return {"answer": f"Пользователь с id {user_id} добавлен в whitelist"}
        return {"answer": False}

    def delete_from_whitelist(self, peer_id: int, text: str, admins: list, logs: dict) -> dict:
        """
        Удаление пользователя из whitelist

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        prefix_size = len("whitelist delete ")
        if text[:prefix_size] == "whitelist delete " and peer_id in admins:
            user_id = int(text[prefix_size:])
            if not len(logs["whitelist"].data[logs["whitelist"].data["user_id"] == user_id].values):
                return {"answer": f"Пользователь с id {user_id} не был в whitelist'е"}
            logs['whitelist'].clear(conditions={'user_id': user_id})
            self.FileLoader().update_csv(self.prefix+"whitelist", logs["whitelist"].data)
            return {"answer": f"Пользователь с id {user_id} удален из whitelist'a"}
        return {"answer": False}

    def ban(self, peer_id: int, text: str, admins: list, logs: dict) -> dict:
        """
        Добавления пользователя в ban list

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower().split(' ')
        if text[0] == 'ban' and peer_id in admins:
            logs["ban_logs"].update(int(text[1]), text[2])
            self.FileLoader().update_csv(self.prefix+"banned", logs["ban_logs"].data)
            return {"answer": "Пользователь забанен"}
        return {"answer": False}

    def unban(self, peer_id, text, admins, logs):
        """
        Разбан пользователя

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower().split(' ')
        if text[0] == 'unban' and peer_id in admins:
            user_id = int(text[1])
            if not len(logs["ban_logs"].data[logs["ban_logs"].data["user_id"] == user_id].values):
                return {"answer": f"Пользователь с id {user_id} не был забанен"}
            logs['ban_logs'].clear(conditions={'user_id': user_id})
            self.FileLoader().update_csv(self.prefix+"banned", logs["ban_logs"].data)
            return {"answer": "Пользователь разбанен"}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def registration(self, peer_id: int, text: str, logs: dict) -> dict:
        """
        Регистрация пользователя (установка курса и группы пользователя)

        Пользователь не сможет пройти регистрацию, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "last_messages" хранится словарь сохраненных сообщений

            По ключу "keyboard" хранится клавиатура для сообщения
        """
        text = text.lower()
        if peer_id not in list(logs['users_groups'].data['user_id']) or 'изменить данные' == text:
            logs['users_groups'].clear(conditions={'user_id': peer_id})
            if self.__answers.get(peer_id) is None or text == "изменить данные":
                text = "изменить данные"
                self.__answers.update({peer_id: [text]})
                return {"answer": "Приветствую! Для продолжения пройдите краткую регистрацию\nВыберите курс",
                        "keyboard": self.Keyboard.json_to_keyboard(self.prefix + "courses_keyboard.json"),
                        "last_messages": self.__answers}

            elif self.__answers[peer_id][0] == "изменить данные" and len(self.__answers[peer_id]) == 1:
                if text in self.Messages().get_courses():
                    self.__answers[peer_id].append(text)
                    course_number = int(self.__answers[peer_id][1][0])
                    return {"answer": "Выберите группу",
                            "keyboard": self.Keyboard.json_to_keyboard(self.prefix + f"course{course_number}_keyboard.json"),
                            "last_messages": self.__answers}
                else:
                    return {"answer": "Для продолжения выберите курс",
                            "keyboard": self.Keyboard.json_to_keyboard(self.prefix + "courses_keyboard.json"),
                            "last_messages": self.__answers}
            elif len(self.__answers[peer_id]) == 2:
                course_number = int(self.__answers[peer_id][1][0])
                if text in self.Messages().get_groups()[course_number - 1]:
                    logs['users_groups'].update(peer_id, self.__answers[peer_id][1], text)
                    self.FileLoader().update_csv(self.prefix+"users_data", logs["users_groups"].data)
                    self.__answers[peer_id].clear()
                    return {"answer": 'Вы успешно прошли регистрацию. Для изменения данных введите "Изменить данные"',
                            "last_messages": self.__answers}
                else:
                    return {"answer": "Для продолжения выберите группу",
                            "keyboard": self.Keyboard.json_to_keyboard(self.prefix + f"course{course_number}_keyboard.json"),
                            "last_messages": self.__answers}
        return {"answer": False}

    @AccessLimiter.ban_check(Configuration)
    def teach_bot(self, peer_id: int, text: str, logs: dict) -> dict:
        """
        Обучение бота новым фразам

        Пользователь не сможет получить ответ на сообщение, если у него будет забанена функция

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "last_messages" хранится словарь сохраненных сообщений
        """
        if text.lower() == "обучить бота":
            self.__answers.update({peer_id: [text.lower()]})
            return {"answer": "Напишите фразу, на которую бот будет отвечать",
                    "last_messages": self.__answers}
        elif self.__answers.get(peer_id) is not None:
            if len(self.__answers[peer_id]) == 1 and self.__answers[peer_id][0] == "обучить бота":
                filtered = BadWordsFilter().filtered(text)
                if filtered != text:
                    self.__answers[peer_id].clear()
                    return {"answer": "Нельзя обучать бота мату",
                            "last_messages": self.__answers}
                text = text.lower()
                custom_file = self.FileLoader(self.Storage).get_csv(self.prefix+"teach")
                if text in list(self.Messages(custom=custom_file).custom['Q']):
                    self.__answers[peer_id].clear()
                    return {"answer": "Этой фразе бот уже обучен",
                            "last_messages": self.__answers}
                elif not self.Messages().is_in_reserve(text):
                    self.__answers[peer_id].append(text)
                    return {"answer": "Напишите фразу, которой бот будет отвечать на введённую вами ранее",
                            "last_messages": self.__answers}
                else:
                    self.__answers[peer_id].clear()
                    return {"answer": "Эта фраза зарезервирована, выберите другую",
                            "last_messages": self.__answers}
            if len(self.__answers[peer_id]) == 2 and self.__answers[peer_id][0] == "обучить бота":
                filtered = BadWordsFilter().filtered(text)
                if filtered != text:
                    self.__answers[peer_id].clear()
                    return {"answer": "Нельзя обучать бота мату",
                            "last_messages": self.__answers}
                self.__answers[peer_id].append(text)
                time_ = datetime.datetime.now()
                Q, A = self.__answers[peer_id][1], self.__answers[peer_id][2]
                logs['teach'].update(peer_id, Q, A, time_)
                self.FileLoader().update_csv(self.prefix+"teach", logs["teach"].data)
                self.__answers[peer_id].clear()
                return {"answer": "Вы успешно обучили бота",
                        "last_messages": self.__answers}
        return {"answer": False}

    def save_now(self, peer_id: int, text: str, admins: list, logs: dict) -> dict:
        """
        Функция для выгрузки логов на диск по команде

        Функция доступна только администраторам

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе
        """
        text = text.lower()
        if text == 'выгрузить логи' and peer_id in admins:
            self.Saver().upload_files(logs, now=True)
            return {"answer": "Логи выгружены на диск"}
        return {"answer": False}

    def get_answer(self, peer_id, text, name, surname, course, group, admins, logs):
        """
        Получения ответа на сообщение

        Функция последовательно вызывает методы класса, когда какой-то метод вернул ответ != False, функция останавливается
        и возвращает этот ответ

        Parameters
        ----------
        peer_id: int
            id пользователя
        text: str
            Текст сообщения
        name: str
            Имя пользователя
        surname: str
            Фамилия пользователя
        course: str
            Номер курса
        group: int
            Номер группы
        admins: list
            Список id администраторов
        logs: dict
            Словарь с объектами класса Logs, хранящий данные о пользователях и сообщениях

        Returns
        -------
        dict
            Словарь с ответом

            По ключу "answer" хранится текстовое сообщение, если на полученное сообщение есть ответ, False иначе

            По ключу "last_messages" хранится словарь сохраненных сообщений

            По ключу "keyboard" хранится клавиатура для сообщения

            По ключу "photo_file" хранится название jpg файла с графиком

            По ключу "photo_link" хранится bool переменная, если True - в "answer" ссылка на изображение
        """
        answer_teach = self.teach_bot(peer_id, text, logs)
        if answer_teach.get("answer"):
            return answer_teach
        answer_photo = self.get_answer_photo(peer_id, text)
        if answer_photo.get("answer"):
            return answer_photo
        answer_command = self.get_answer_command(peer_id, text)
        if answer_command.get("answer"):
            return answer_command
        answer_text = self.get_answer_text(peer_id, text)
        if answer_text.get("answer"):
            return answer_text
        answer_links = self.get_answer_links(peer_id, text, course)
        if answer_links.get("answer"):
            return answer_links
        answer_schedule = self.get_answer_schedule(peer_id, text, course, group)
        if answer_schedule.get("answer"):
            return answer_schedule
        answer_teacher_info = self.get_teacher_info(peer_id, text, name, surname, admins)
        if answer_teacher_info.get("answer"):
            return answer_teacher_info
        answer_query = self.get_answer_query(peer_id, text)
        if answer_query.get("answer"):
            return answer_query
        answer_graph = self.get_answer_graph(peer_id, text)
        if answer_graph.get("answer"):
            return answer_graph
        answer_code = self.get_answer_code(peer_id, text)
        if answer_code.get("answer"):
            return answer_code
        answer_add_to_whitelist = self.add_to_whitelist(peer_id, text, admins, logs)
        if answer_add_to_whitelist.get("answer"):
            return answer_add_to_whitelist
        answer_delete_from_whitelist = self.delete_from_whitelist(peer_id, text, admins, logs)
        if answer_delete_from_whitelist.get("answer"):
            return answer_delete_from_whitelist
        answer_registration = self.registration(peer_id, text, logs)
        if answer_registration.get("answer"):
            return answer_registration
        answer_ban = self.ban(peer_id, text, admins, logs)
        if answer_ban.get("answer"):
            return answer_ban
        answer_unban = self.unban(peer_id, text, admins, logs)
        if answer_unban.get("answer"):
            return answer_unban
        answer_delete_text = self.delete_answer_text(peer_id, text, admins, logs)
        if answer_delete_text.get("answer"):
            return answer_delete_text
        answer_save_now = self.save_now(peer_id, text, admins, logs)
        if answer_save_now.get("answer"):
            return answer_save_now
        return {"answer": False}

