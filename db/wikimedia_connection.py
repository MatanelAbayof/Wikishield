import toolforge
from db.db_connection import BaseDbConnection
from lang.langs import Lang


# ------------------------------------------------------------------------------------------------------------
class DBConnection(BaseDbConnection):

    def __init__(self, sql_user_name: str, lang: Lang):
        """
        initialize connection to Wikimedia database

        param sql_user_name: SQL user name

        param lang: language
        """

        super().__init__()
        self.sql_user_name = sql_user_name
        self.lang = lang

    def _get_db_name(self):
        """
        return default database name
        """

        return '{}wiki_p'.format(self.lang.name)

    def _connect(self):
        """
        connect to DB
        """

        self.ctx = toolforge.connect(self._get_db_name()) 