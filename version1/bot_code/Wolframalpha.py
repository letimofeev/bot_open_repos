import wolframalpha
import requests
from Settings import *


class WolframalphaAPI:
    """Класс для получения ответа на запросы с помощью Wolframalpha

    Attributes
    ----------
    app_id: str
        id выданный wolframalpha для подключения
    client: wolframalpha.Client
        Объект библиотеки wolframalpha для взаимодействия с сервисом

    """
    def __init__(self):
        self.app_id = Constants.w_appid.value
        self.client = wolframalpha.Client(self.app_id)

    @staticmethod
    def rename_operations(func_str: str) -> str:
        """
        Замена символов "+" и "-" на слова (особенность вольфрама при работе с функцией для графика)

        Parameters
        ----------
        func_str: str
            Функция в строковом формате

        Returns
        -------
        str
            Функция с замененными символами
        """
        operations = {'+': ' plus ', '-': ' minus '}
        for i in range(len(operations)):
            symbol = list(operations.keys())[i]
            func_str = func_str.replace(symbol, operations[symbol])

        return func_str

    def query(self, text: str) -> str:
        """
        Обработка запроса вольфрамом

        Parameters
        ----------
        text: str
            Запрос, который нужно выполнить
        Returns
        -------
        str
            Результат выполнения запроса

        Examples
        --------
        >>> WolframalphaAPI().query("lol")
        'LOL (acronym)\\nlaugh out loud\\nlaughing out loud\\nlots of love\\nlots of laughter\\n'

        >>> WolframalphaAPI().query("x + y = 4")
        'x + y = 4\\nline\\nx + y - 4 = 0\\ny = 4 - x\\ny = 4 - x\\ny = 4 - x\\n'
        """
        res = self.client.query(text)
        res_list = []
        for pod in res.pods:
            for sub in pod.subpods:
                if sub.plaintext is not None:
                    res_list.append(f"{sub.plaintext}\n")

        return ''.join(res_list)

    def get_plot_url(self, func: str, dimension: str = "") -> str:
        """
        Получение url изображения с графиком функции

        Parameters
        ----------
        func: str
            Функция, график которой нужно построить
        dimension: str, default ""
            Количество переменных функции

        Returns
        -------
        str
            url изображения
        """
        query = f"plot {func}"
        query_url = f"http://api.wolframalpha.com/v2/query?" \
                    f"appid={self.app_id}" \
                    f"&input={query}" \
                    f"&output=json" \
                    f"&includepodid={dimension}Plot" \

        r = requests.get(query_url).json()

        pods = r["queryresult"]["pods"]
        plot_url = pods[0]["subpods"][0]["img"]["src"]

        return plot_url

    def save_plot(self, func: str, dimension: str, graph_name: str) -> None:
        """
        Сохранение графика функции в jpg

        Parameters
        ----------
        func: str
            Функция, график которой нужно построить
        dimension: str
            Количество переменных функции
        graph_name: str
            Имя файла, с которым изображение будет сохранено

        Returns
        -------
        None
        """
        if dimension == 2:
            dimension = f""
        elif dimension == 3:
            dimension = f"3D"
        func = self.rename_operations(func)
        plot_url = self.get_plot_url(func, dimension)
        img_name = f"{graph_name}.jpg"
        img_data = requests.get(plot_url).content
        with open(img_name, 'wb') as handler:
            handler.write(img_data)

