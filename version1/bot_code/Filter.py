from Interpreter import Interpreter


class BadWordsFilter:
    """
    Класс BadWordsFilter для фильтрации запрещенных слов
    """

    @staticmethod
    def filtered(text: str) -> str:
        """
        Функция, заменяющая запрещенные слова на *

        Parameters
        ----------
        text: str
            Сообщение, который нужно отфильтровать

        Returns
        -------
        str
            Отфильтрованное сообщение

        Examples
        --------
        >>> BadWordsFilter.filtered("xyi")
        '***'

        Количество звездочек не всегда соответсвует количеству символов в слове

        >>> BadWordsFilter.filtered("Pи3да")
        '********'

        >>> BadWordsFilter.filtered("xYet4")
        '******'

        Пропускает некоторые комбинации

        >>> BadWordsFilter.filtered("blyat'")
        "blyat'"

        >>> BadWordsFilter.filtered("3bлан'")
        "3bлан'"
        """
        filtered = Interpreter(language='php',
                               prefix='<?php\n',
                               type_='.php').execute_code(args=text, filename='filter.php').replace("⠀", ' ')
        return filtered

