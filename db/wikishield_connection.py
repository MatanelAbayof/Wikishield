import toolforge
from db.db_connection import BaseDbConnection


# ------------------------------------------------------------------------------------------------------------
class DBConnection(BaseDbConnection):
    _HOST = 'tools.db.svc.eqiad.wmflabs'

    def __init__(self, sql_user_name: str='s54207'): #TODO: get user name from file
        """
        initialize connection to Wikishield database
        """

        super().__init__()
        self.sql_user_name = sql_user_name

    def _get_db_name(self):
        return self.sql_user_name + '__wikishield_p'

    def _connect(self):
        """
        connect to DB
        """

        args = { 'host': self._HOST }
        self.ctx = toolforge.connect(self._get_db_name(), **args) 