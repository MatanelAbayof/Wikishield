import toolforge
from db.db_connection import BaseDbConnection
import pymysql
from pymysql.constants import FIELD_TYPE


# ------------------------------------------------------------------------------------------------------------
class DBConnection(BaseDbConnection):
    _HOST = 'tools.db.svc.eqiad.wmflabs'

    def __init__(self, sql_user_name: str):
        """
        initialize connection to Wikishield database

        param sql_user_name: SQL user name
        """

        super().__init__()
        self.sql_user_name = sql_user_name

    def _get_db_name(self):
        """
        return default database name
        """

        return self.sql_user_name + '__wikishield_p'

    def _connect(self):
        """
        connect to DB
        """


        orig_conv = pymysql.converters.conversions
        #Adding support for bit data type
        orig_conv[FIELD_TYPE.BIT] = lambda data: data == b'\x01'

        args = { 'host': self._HOST, 'conv': orig_conv }
        self.ctx = toolforge.connect(self._get_db_name(), **args) 