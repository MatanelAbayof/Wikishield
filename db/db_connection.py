from pymysql.connections import Connection
from abc import ABC, abstractmethod
import time


class BaseDbConnection(ABC):
    """
    this is a base class for database connection
    """

    _MAX_CONNECTION_TIRES = 10

    def __init__(self):
        """
        initialize connection 
        """

        self.ctx: Connection = None # TODO: fix this (Syntax error in Python 3.5)

    def start(self):
        """
        start connection to DB
        """

        tries = 0
        while tries < self._MAX_CONNECTION_TIRES:
            try:
                self._connect()
                return
            except:
                tries += 1
                print("failed to connect DB with try num {}".format(tries)) #TODO: remove this
                time.sleep(5)
        raise ConnectionError("Cannot connect to DB")

    @abstractmethod
    def _connect(self):
        """
        connect to DB
        """

        pass

    def restart(self):
        """
        restart connection to DB
        """

        self.close()
        self.start()

    def close(self):
        """
        close connection
        """

        if self.ctx is not None:
            self.ctx.close()
