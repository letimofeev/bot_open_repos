import requests
from abc import ABCMeta, abstractmethod, ABC

import wolframalpha

from settings import WolframalphaAPISettings, logger


class IRequestHandler(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_response(self, text: str) -> str:
        raise NotImplementedError


class IGraphBuilder(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_plot(self, func: str, var_num: int, graph_name: str) -> bool:
        raise NotImplementedError


class WolframalphaAPI(IRequestHandler, IGraphBuilder):
    def __init__(self):
        self.app_id = WolframalphaAPISettings.TOKEN
        self.client = self.get_connection()

    def get_connection(self):
        return wolframalpha.Client(app_id=self.app_id)

    def get_response(self, text: str) -> str:
        try:
            res = self.client.query(text)
        except Exception:
            logger.error("Connection to WolframalphaAPI failed", exc_info=True)
            return ""
        res_list = []
        for pod in res.pods:
            for sub in pod.subpods:
                if sub.plaintext is not None:
                    res_list.append(f"{sub.plaintext}\n")
        logger.debug("get_response(): status message: %s", "OK")
        return "".join(res_list)

    @staticmethod
    def rename_operations(func_str: str) -> str:
        return func_str.replace("+", "%2B")

    @staticmethod
    def get_dimension(var_num: int) -> str:
        dimension = {1: "", 2: "3D"}
        return dimension.get(var_num)

    def get_plot_url(self, func: str, dimension: str = "") -> str:
        query = f"plot {func}"
        query_url = f"http://api.wolframalpha.com/v2/query?" \
                    f"appid={self.app_id}" \
                    f"&input={query}" \
                    f"&output=json" \
                    f"&includepodid={dimension}Plot"
        r = requests.get(query_url).json()
        try:
            pods = r["queryresult"]["pods"]
            plot_url = pods[0]["subpods"][0]["img"]["src"]
        except KeyError:
            return ""
        logger.debug("get_plot_url(): status message: %s", "OK")
        return plot_url

    def save_plot(self, func: str, var_num: int, graph_name: str = "graph") -> bool:
        plot_url = self.get_plot_url(self.rename_operations(func), self.get_dimension(var_num))
        if not plot_url:
            return False
        if graph_name[-4:] == ".jpg":
            img_name = graph_name
        else:
            img_name = f"{graph_name}.jpg"
        img_data = requests.get(plot_url).content
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        logger.debug("save_plot(): status message: %s", "OK")
        return True

