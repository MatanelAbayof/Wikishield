import toolforge
from db.db_connection import BaseDbConnection


# ------------------------------------------------------------------------------------------------------------
class DBConnection(BaseDbConnection):

    def __init__(self):
        """
        initialize connection to Wikishield database
        """

        super().__init__()

    def _connect(self):
        """
        connect to DB
        """

        args = { 'host': 'tools.db.svc.eqiad.wmflabs' }
        self.ctx = toolforge.connect('s54207__wikishield_p', **args)