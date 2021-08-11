from typing import NamedTuple

from user import SQLUser
from messages import SQLMessages
from records_links import PandasLink
from schedule import PandasSchedule
from request_handler import WolframalphaAPI
from filter import PHPFilter


class Config(NamedTuple):
    user = SQLUser
    messages = SQLMessages
    links = PandasLink
    schedule = PandasSchedule
    request_handler = WolframalphaAPI
    graph_builder = WolframalphaAPI
    filter = PHPFilter

