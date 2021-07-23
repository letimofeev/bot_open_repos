import inspect
import numpy as np


class AccessLimiter:
    """
    Класс декораторов для ограничения доступа к функциями бота
    """

    @staticmethod
    def whitelist_check(conf):
        """
        Контроль доступа к функциям требующих наличия пользователя в whitelist'е

        Parameters
        ----------
        conf: configuration
            Класс конфирурации

        Returns
        -------
        Результат выполнения функции, если пользователь есть в whitelist'е, отрицательный ответ иначе
        """
        def decorator(func):
            def wrapped(self, *args, **kwargs):
                whitelist_data = conf.FileLoader(conf.Storage).get_csv(file_name=conf.prefix+"whitelist")
                args_arr = np.array(inspect.getfullargspec(func)[0])
                id_pos = np.argwhere(args_arr == 'peer_id')[0][0]
                peer_id = args[id_pos - 1]
                whitelist = whitelist_data['user_id'].values
                if peer_id in whitelist:
                    res = func(self, *args, **kwargs)
                    if res.get("answer"):
                        return res
                    else:
                        return {"answer": False}
                else:
                    return {"answer": False}
            return wrapped
        return decorator

    @staticmethod
    def ban_check(conf):
        """
        Контроль доступа к функциям

        Parameters
        ----------
        conf: configuration
            Класс конфирурации

        Returns
        -------
        Результат выполнения функции, если пользователя нет в ban'е, иначе сообщение о том, что пользователю ограничен доступ
        """
        def decorator(func):
            def wrapped(self, *args, **kwargs):
                args_arr = np.array(inspect.getfullargspec(func)[0])
                id_pos = np.argwhere(args_arr == 'peer_id')[0][0]
                peer_id = args[id_pos - 1]
                ban_data = conf.FileLoader(conf.Storage).get_csv(file_name=conf.prefix+"banned")
                ban_list = ban_data[ban_data['user_id'] == peer_id]['banned_functions'].values
                res = func(self, *args, **kwargs)
                if res.get("answer"):
                    if func.__name__ in ban_list:
                        return {"answer": "Администрация временно ограничила ваше право пользования этой функцией"}
                    else:
                        return res
                else:
                    return {"answer": False}
            return wrapped
        return decorator

