from abc import ABCMeta, abstractmethod, ABC

from code_executor import PHPExecutor


class IFilter(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def filtered(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_allowed(self, text: str) -> bool:
        raise NotImplementedError


class PHPFilter(IFilter):
    def __init__(self, filename):
        self.script_name = filename
        self.executor = PHPExecutor

    def filtered(self, text: str) -> str:
        return self.executor(self.script_name).execute_code(args=text)

    def is_allowed(self, text: str) -> bool:
        return text == self.executor(self.script_name).execute_code(args=text)
