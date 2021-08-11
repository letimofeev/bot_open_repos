import psycopg2
from psycopg2 import OperationalError

from settings import logger, PostgresSQLSettings


class PostgreSQL:
    def __init__(self):
        self.database = PostgresSQLSettings.DB_NAME
        self.user = PostgresSQLSettings.DB_USERNAME
        self.password = PostgresSQLSettings.DB_PASSWORD
        self.host = PostgresSQLSettings.DB_HOST
        self.port = PostgresSQLSettings.DB_PORT
        self.connection = self.get_connection()

    def get_connection(self):
        connection = None
        try:
            connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except OperationalError:
            logger.error("Connection to PostgreSQL DB failed", exc_info=True)
            raise
        finally:
            return connection

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
        except OperationalError:
            logger.error("execute_query(): Exception occurred", exc_info=True)
            raise
        else:
            self.connection.commit()

    def execute_read_query(self, query, one=False):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
        except OperationalError:
            logger.error("execute_read_query(): Exception occurred", exc_info=True)
            raise
        else:
            if one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        finally:
            return result

