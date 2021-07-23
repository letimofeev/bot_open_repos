import subprocess


class Interpreter:
    """Класс для получения результата выполнения кода

    Attributes
    ----------
    language: str
        Язык программирования
    type_: str
        Расширение файла с кодом
    prefix: str, default ""
        Префикс кода
    default_filename: str
        Название файла с которым сохраняется код по умолчанию
    """
    def __init__(self, language: str, type_: str, prefix: str = ""):
        self.language = language
        self.type_ = type_
        self.prefix = prefix
        self.default_filename = f'{self.language}_code{self.type_}'

    @staticmethod
    def replace_out(text: str) -> str:
        """
        Замена проблема на символ пробела, который не будет пропускаться

        Parameters
        ----------
        text: str
            Текст, в котором нужно заменить пробелы

        Returns
        -------
        str
            Текст с замененными пробелами
        """
        return text.replace(' ', "⠀")

    @staticmethod
    def reformat_code(text: str) -> str:
        """
        Замена символов, изменяемых вк

        Parameters
        ----------
        text: str
            Текст кода

        Returns
        -------
        str
            Измененный текст кода
        """
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
        text = text.replace('\\t', '\t').replace('\\n', '\n')
        return text

    def save_as_file(self, code: str) -> None:
        """
        Сохранение строки кода как файл

        Parameters
        ----------
        code: str
            Строка с кодом

        Returns
        -------
        None
        """
        with open(f'{self.language}_code{self.type_}', 'w', encoding='utf-8') as file:
            file.write(code)

    def submit(self, code: str, args: str, filename: str) -> subprocess.Popen:
        """
        Создание процесса выполнения кода

        Parameters
        ----------
        code: str
            Строка с кодом
        args: str
            Строка с аргументами для кода
        filename: str
            Имя файла, который нужно выполнить

        Returns
        -------
        subprocess.Popen
            Процесс командной строки
        """
        if code is not None:
            code = self.prefix + code
            code = self.reformat_code(code)
            self.save_as_file(code)
        if filename is None:
            filename = self.default_filename
        proc = subprocess.Popen(f'{self.language} ' + filename + ' ' + args, shell=True, stdout=subprocess.PIPE)
        return proc

    def execute_code(self, code: str = None, args: str = '', filename: str = None) -> str:
        """
        Выполнение кода

        Parameters
        ----------

        code: str, default None
            Строка с кодом
        args: str, default ""
            Строка с аргументами для кода
        filename: str, default None
            Имя файла с кодом

        Returns
        -------
        str
            Строка с результатом выполнения кода

        Examples
        --------

        Выполнение php кода

        >>> text_code = "echo 10;"
        >>> Interpreter("php", ".php", "<?php\\n").execute_code(text_code)
        '10'

        Передача аргументов

        >>> text_code = "$text = ''; for ($i = 1; $i < count($argv); ++$i) {$text .= $argv[$i] . ' ';} echo $text;"
        >>> Interpreter("php", ".php", '<?php\\n').execute_code(code=text_code, args="1 2 3 4")
        '1⠀2⠀3⠀4⠀'

        При возникновении ошибки php возвращает строку с ошибкой

        >>> text_code = ":)"
        >>> Interpreter("php", ".php", '<?php\\n').execute_code(code=text_code, args="1 2 3 4")
        '\\nParse⠀error:⠀syntax⠀error,⠀unexpected⠀token⠀":",⠀expecting⠀end⠀of⠀file⠀in⠀C:\\Users\\timof\\php_code.php⠀on⠀line⠀2\\n'

        Выполнение python кода

        >>> text_code = "print(__import__('sys').argv[1:])"
        >>> Interpreter("python", ".py").execute_code(code=text_code, args="1 2 3 4")
        "['1',⠀'2',⠀'3',⠀'4']\\r\\n"

        При возникновении ошибки python возвращает пустую строку

        >>> text_code = "mem 1i2ek"
        >>> Interpreter("python", ".py").execute_code(code=text_code, args="1 2 3 4")
        ''

        При передаче неверного языка в конструктор класса, функция возвращает пустую строку

        >>> text_code = "print(100)"
        >>> Interpreter("pycon", ".py").execute_code(code=text_code, args="memes")
        ''

        При указании неверного типа функция продолжает возвращать правильный результат.
        Но так делать не рекомендуется

        >>> text_code = "print(1 < 2 < 3)"
        >>> Interpreter("python", ".php").execute_code(code=text_code)
        'True\\r\\n'

        >>> text_code = "echo $argv[1];"
        >>> Interpreter("php", ".)))", '<?php\\n').execute_code(code=text_code, args="'meme'")
        "'meme'"

        """
        proc = self.submit(code, args, filename)
        script_response = proc.stdout.read()
        return self.replace_out(script_response.decode("utf-8"))

