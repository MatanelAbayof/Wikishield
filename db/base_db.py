from abc import ABC, abstractmethod
from datetime import datetime, date

from pymysql.connections import Connection
from pymysql.cursors import Cursor

from lang.langs import LangsManager, Lang


class BaseDB(ABC):
    """
    this is a base class for database operations
    """

    def __init__(self, ctx: Connection, lang: Lang):
        """
        initialize
        """

        self.lang = lang
        self.ctx = ctx

    @abstractmethod
    def db_name(self):
        """
        return database name
        """

        pass

    def set_max_allowed_packet(self, n: int = 67108864):
        """
        set maximum allowed packet in database

        this prevents "Lost connection" exception when update big data that bigger than `max_allowed_packet`

        for more info see `https://dev.mysql.com/doc/refman/8.0/en/packet-too-large.html`

        param n: the maximum allowed packet
        """
        query = "SET GLOBAL max_allowed_packet = {}".format(int(n))
        self._exec(query)

    def set_safe_updates(self, safe: bool = True):
        """
        enable/disable safe updates or deletes in database

        in MySQL "safe" means that you can execute updates queries just if they indexable

        param safe: if True use safe. False otherwise
        """

        query = "SET SQL_SAFE_UPDATES = {}".format(int(safe))

        self._exec(query)

    def _exec(self, query: str, args=None, exec_many: bool = False):
        """
        execute a query

        param query: the query

        param exec_many: True if execute many. False otherwise

        param args: parameters used with query. (optional)
        """

        cursor = self.__open_cursor()
        if exec_many:
            cursor.executemany(query, args)
        else:
            cursor.execute(query, args)
        cursor.close()

    def _fetchall(self, query: str, args=None, as_dict: bool = False):
        """
        fetch all records from query

        param query: the query

        param args: parameters used with query. (optional)

        param as_dict: if True - each row will be a directory. otherwise - each row will be a list

        return fetch result as array
        """

        cursor = self.__open_cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()

        if as_dict:
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
        else:
            results = rows

        cursor.close()
        return results

    def _lazy_fetchall(self, query: str, args=None):
        """
        fetch all records from query with lazy

        this is usefull function to save memory

        warning: don't do another execute to dataset while this fetch not finished.
        if you want to fetch many rows, and do another execule in parallel you need to open new connection (DB connection it's thread safe)

        param query: the query

        param args: parameters used with query. (optional)

        return generator of all records
        """

        cursor = self.__open_cursor()
        cursor.execute(query, args)
        for row in cursor:
            yield row
        cursor.close()

    def commit(self):
        """
        commit changes in database
        """
        self.ctx.commit()

    def __open_cursor(self) -> Cursor:
        """
        open a new cursor

        return the cursor
        """

        return self.ctx.cursor()

    @staticmethod
    def parse_timestamp(timestamp_str: str):
        """
        parse a datetime object from timestamp string

        param timestamp_str: timestamp string

        return datetime
        """

        return datetime.strptime(timestamp_str.decode("utf-8"), '%Y%m%d%H%M%S')

    @staticmethod
    def to_timestamp_cell(dt: date):
        """
        convert a datetime to timestamp string

        param dt: the datetime

        return timestamp string
        """

        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def clone_timestamp_cell(timestamp_str: str):
        """
        clone timestamp string to timestamp cell

        param timestamp_str: timestamp string

        return copy of timestamp string
        """

        return BaseDB.to_timestamp_cell(BaseDB.parse_timestamp(timestamp_str))

    @staticmethod
    def create_placeholders(n: int):
        """
        create place holders of query in format "%s, ..., %s" when number of "%s" is `n`

        param n: the number of the place holders

        return string of the place holders
        """

        return ", ".join(["%s"] * n) if n > 0 else ""
