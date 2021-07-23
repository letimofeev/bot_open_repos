from Bot import *
import threading
from Configuration import Configuration as Cfg


try:
    if Cfg.BotPlatform == "VKBot":
        bot = VkBot()
    elif Cfg.BotPlatform == "TGBot":
        bot = TgBot()
    t = threading.Thread(target=Cfg.Saver().upload_files, args=(bot.logs, ))
    t.start()
    bot.start()
except Exception as e:
    time_ = str(datetime.datetime.now())
    error = pd.DataFrame.from_dict({
        'time:': [time_],
        'error_code:': [type(e).__name__],
        'traceback:': [traceback.format_exc()]})
    error.to_csv("errors_main.csv")
