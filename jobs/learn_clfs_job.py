from ttictoc import TicToc

from clf.wiki_classifier import WikiClassifier
from db.wikishield_connection import DBConnection as WS
from lang.langs import LangsManager
from jobs.base_job import BaseJob
from db.connection_info import read_sql_user_name


class LearnClfsJob(BaseJob):
    """
    this is a job manager that learn classifiers and update pickles
    """

    def __init__(self):
        """
        initialize the class
        """

        super().__init__()

    def start(self):
        """
        start the job

        the job includes the following things:

            * fetch new unverified revisions
            * score this revisions
            * filter all suspected bad revisions
            * insert revisions to table
        """

        t = TicToc()
        t.tic()

        sql_user_name = read_sql_user_name()
        wikishield_conn = WS(sql_user_name)
        wikishield_conn.start()
        lm = LangsManager()
        for lang_name in lm.langs_names:
            lang = lm.get_lang(lang_name)
            clf = WikiClassifier(lang, wikishield_conn.ctx)
            limit = None
            clf.learn(limit) # TODO: needs a full learning
            file_path = WikiClassifier.PICKLE_FOLDER_PATH + '/' + lang_name + '.pickle'
            clf.pickle_to_file(file_path)

        wikishield_conn.close()

        t.toc()
        print("learn job summary: elapsed time = ", t.elapsed, "seconds") #TODO: remove this
