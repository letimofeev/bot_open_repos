import datetime
import json
from abc import ABCMeta, abstractmethod, ABC

from psycopg2 import sql

from postgres import PostgreSQL as pSQL


class IUser(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def log_user(self, user_id, name, surname):
        raise NotImplementedError

    @abstractmethod
    def registration(self, course=None, group=None):
        raise NotImplementedError

    @abstractmethod
    def get_teacher_info(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def get_reg_info(self):
        raise NotImplementedError

    @abstractmethod
    def set_status(self, status, callback=None):
        raise NotImplementedError

    @abstractmethod
    def get_status(self):
        raise NotImplementedError

    @abstractmethod
    def get_callback(self):
        raise NotImplementedError

    @abstractmethod
    def reset_all_statuses(self):
        raise NotImplementedError

    @abstractmethod
    def ban_check(self):
        raise NotImplementedError

    @abstractmethod
    def ban(self):
        raise NotImplementedError

    @abstractmethod
    def unban(self):
        raise NotImplementedError


class SQLUser(IUser):
    def __init__(self, table_name, user_id=None):
        self.user_id = user_id
        self.SQL = pSQL
        self.TableName = table_name

    def log_user(self, user_id, name, surname):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({user_id}, {name}, {surname}, {time})
        ON CONFLICT (user_id) DO NOTHING;
        """).format(
            table_name=sql.Identifier(self.TableName.USERS),  # sql.Identifier нужен для предотвращения SQL инъекций
            user_id=sql.Literal(user_id),
            name=sql.Literal(name),
            surname=sql.Literal(surname),
            time=sql.Literal(datetime.datetime.now())
        )
        self.SQL().execute_query(query)

    def registration(self, course=None, group=None):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({user_id}, {user_course}, {user_group})
        ON CONFLICT (user_id) DO
        UPDATE
        SET user_course = {user_course}, user_group = {user_group}
        WHERE {table_name}.user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.REG_INFO),
            user_id=sql.Literal(self.user_id),
            user_course=sql.Literal(course),
            user_group=sql.Literal(group)
        )
        self.SQL().execute_query(query)

    def get_teacher_info(self, text: str):
        query_id = sql.SQL("""
        SELECT user_id, answer FROM {table_name}
        WHERE text = {message};
        """).format(
            table_name=sql.Identifier(self.TableName.CUSTOM_ANSWERS),
            message=sql.Literal(text)
        )
        res = self.SQL().execute_read_query(query_id, one=True)
        if res is None:
            return None
        user_id, answer = res
        query_name = sql.SQL("""
        SELECT name, surname FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.USERS),
            user_id=sql.Literal(user_id),
        )
        res = self.SQL().execute_read_query(query_name, one=True)
        if res is None:
            return user_id, None, None, answer
        name, surname = res
        return user_id, name, surname, answer

    def get_reg_info(self):
        query = sql.SQL("""
        SELECT user_course, user_group FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.REG_INFO),
            user_id=sql.Literal(self.user_id)
        )
        return self.SQL().execute_read_query(query, one=True)

    def set_status(self, status, callback=None):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({user_id}, {status}, {callback})
        ON CONFLICT (user_id) DO
        UPDATE
        SET status = {status}, callback = {callback}
        WHERE {table_name}.user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.USER_STATUS),
            user_id=sql.Literal(self.user_id),
            status=sql.Literal(status),
            callback=sql.Literal(json.dumps(callback))
        )
        self.SQL().execute_query(query)

    def get_status(self):
        query = sql.SQL("""
        SELECT status FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.USER_STATUS),
            user_id=sql.Literal(self.user_id)
        )
        status = self.SQL().execute_read_query(query, one=True)
        if status:
            return status[0]

    def get_callback(self):
        query = sql.SQL("""
        SELECT callback FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.USER_STATUS),
            user_id=sql.Literal(self.user_id)
        )
        callback = self.SQL().execute_read_query(query, one=True)
        if callback:
            return json.loads(callback[0])

    def reset_all_statuses(self):
        query = sql.SQL("""
        UPDATE {table_name}
        SET status = 'any', callback = NULL
        WHERE TRUE;
        """).format(
            table_name=sql.Identifier(self.TableName.USER_STATUS)
        )
        self.SQL().execute_query(query)

    def ban_check(self):
        query = sql.SQL("""
        SELECT user_id FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.BAN_LIST),
            user_id=sql.Literal(self.user_id)
        )
        return self.SQL().execute_read_query(query, one=True)

    def ban(self):
        query = sql.SQL("""
        INSERT INTO {table_name}
        VALUES ({user_id})
        ON CONFLICT (user_id) DO NOTHING;
        """).format(
            table_name=sql.Identifier(self.TableName.BAN_LIST),
            user_id=sql.Literal(self.user_id)
        )
        self.SQL().execute_query(query)

    def unban(self):
        query = sql.SQL("""
        DELETE FROM {table_name}
        WHERE user_id = {user_id};
        """).format(
            table_name=sql.Identifier(self.TableName.BAN_LIST),
            user_id=sql.Literal(self.user_id)
        )
        self.SQL().execute_query(query)
