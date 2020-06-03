from ttictoc import TicToc

import db.connections_manager as conn_mng
from utils.algorithms import extract_added_words
from clf.wiki_classifier import WikiClassifier
from lang.langs import Lang
from jobs.base_job import BaseJob


class AddRevsJob(BaseJob):
    """
    this is a job manager that add revisions to database
    """

    # minimum bad score to add to database for human verify
    _MIN_BAD_SCORE = 0.0 # TODO: change this to 0.5+-
    # number of revisions to fetch
    _NUM_REVS = 50
    # scalar for extra part size to fetch by the formula: new_part_size = _EX_PART_SIZE*part_size
    _EX_PART_SIZE = 2
    # minimum part size to fetch, for effectivity
    _MIN_PART_SIZE = 10

    def __init__(self, lang: Lang):
        """
        initialize the class

        param lang: language

        param local_conn: local database connection

        param wiki_conn: Wikimedia database connection
        """

        super().__init__()
        self.lang = lang
    
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

        local_conn, wiki_conn = conn_mng.open_connections(self.lang)
        file_path = WikiClassifier.PICKLE_FOLDER_PATH + '/' + self.lang.name + '.pickle'
        wiki_classifier = WikiClassifier.from_pickle_file(file_path)

        wikimedia_db, wikishield_db, wikimedia_api = conn_mng.init_sources(wiki_conn.ctx, local_conn.ctx, self.lang)
        
        max_rev_id = None

        revs, _ = wikimedia_db.fetch_natural_revs(self.lang, self._NUM_REVS, max_rev_id,
                                                  self._EX_PART_SIZE, self._MIN_PART_SIZE)

        for rev in revs:
            diff_text, page_title = wikimedia_api.fetch_rev_diff(rev['wiki_id'], rev['parent_id'])
            rev['page_title'] = page_title
            print(rev)
            words_content = extract_added_words(self.lang, diff_text)
            if len(words_content) > 0:
                score = wiki_classifier.score_rev(words_content)
                rev['score'] = bad_score = score[0]
                if bad_score >= self._MIN_BAD_SCORE:
                    wikishield_db.insert_rev(rev, diff_text, words_content)
        wikishield_db.commit()

        conn_mng.close_connections(local_conn, wiki_conn)

        t.toc()
        print("add_revs_job: elapsed time = ", t.elapsed, "seconds") #TODO: remove this
