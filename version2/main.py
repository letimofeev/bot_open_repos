import signal
import sys

from bot import VkBot
from settings import VKTableName
from answer_config import Config


def before_interrupt():
    Config.user(VKTableName).reset_all_statuses()
    print("User statuses reset to default")


def signal_handler(sig, frame):
    before_interrupt()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

VkBot(Config).start()
