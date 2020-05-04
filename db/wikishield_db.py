from typing import List

from pymysql.connections import Connection

from utils.algorithms import extract_added_words
from db.base_db import BaseDB
from lang.langs import Lang


class WikishieldDB(BaseDB):
    """
    this class manage requests for Wikishield database
    """

    def __init__(self, ctx: Connection, lang: Lang, sql_user_name: str):
        """
        initialize Wikishield database

        param ctx: connection context

        param lang: language

        param sql_user_name: SQL user name
        """

        super().__init__(ctx, lang)
        self.set_safe_updates(safe=False)  # need this for delete
        #TODO: self.set_max_allowed_packet()
        self.sql_user_name = sql_user_name

    @property
    def db_name(self):
        """
        return database name
        """

        return self.sql_user_name + '__wikishield_p'

    @property
    def db_table_name(self):
        """
        return database table name
        """

        return '{}_revisions'.format(self.lang.name)

    def drop_db(self):
        """
        drop database if exists
        """

        query = "DROP DATABASE IF EXISTS `{}`;".format(self.db_name)
        self._exec(query)

    def create_db(self):
        """
        create a new database

        if dataset exists, it's will be loss all data
        """

        self.drop_db()
        query = "CREATE DATABASE `{}`;".format(self.db_name)
        self._exec(query)

    def create_tables(self):
        """
        create tables of Wikishield database
        """

        query = '''CREATE TABLE IF NOT EXISTS `{0}`.`{1}` (
                    `id` INT NOT NULL AUTO_INCREMENT,
                    `wiki_id` INT NOT NULL,
                    `page_id` INT NOT NULL,
                    `page_title` TEXT NULL,
                    `parent_id` INT NOT NULL,
                    `diff` LONGTEXT NULL,
                    `content` LONGTEXT NULL,
                    `timestamp` TIMESTAMP(1) NOT NULL,
                    `user_id` INT NOT NULL,
                    `good_editing` BIT NULL,
                    `score` FLOAT NULL,
                    `trained` BIT NOT NULL DEFAULT 0,
                    PRIMARY KEY (`id`),
                    UNIQUE INDEX `wiki_id_UNIQUE` (`wiki_id` ASC) VISIBLE);
                    '''.format(self.db_name, self.db_table_name)  # TODO: remove `diff` & 'trained'??
        self._exec(query)

    def update_rev(self, rev_wiki_id: int, diff_text: str, content: str, page_title: str):
        """
        update revision data

        param rev_wiki_id: Wikimedia id of revision

        param diff_text: the HTML different string of revision

        param content: the content that extracted from `diff_text`

        param page_title: page title of revision
        """

        query = '''UPDATE `{0}`.`{1}` SET
                    `diff` = %s,
                    `content` = %s,
                    `page_title` = %s
                    WHERE `wiki_id` = %s'''.format(self.db_name, self.db_table_name)
        args = (diff_text, content, page_title, rev_wiki_id)
        self._exec(query, args=args)

    def insert_training_revs(self, revs: List):
        """
        insert revisions to `training_revisions` table

        if revision already exist (i.e. the revision have a same `wiki_id` field) it's not inserted to table

        param revs: list of revisions
        """

        args = list(map(lambda row: (
            row['wiki_id'], row['page_id'], row['parent_id'], BaseDB.clone_timestamp_cell(row['timestamp']),
            int(row['user_id'])), revs))
        query = '''INSERT IGNORE INTO `{0}`.`{1}`
                (`wiki_id`, `page_id`, `parent_id`, `timestamp`, `user_id`) 
                VALUES (%s, %s, %s, %s, %s)'''.format(self.db_name, self.db_table_name)
        self._exec(query, args=args, exec_many=True)
        self.commit()

    def delete_empty_revs(self):
        """
        delete all revisions with empty content in training_revisions table
        """

        query = '''DELETE FROM `{0}`.`{1}` 
                   WHERE `content` = "" OR `content` IS NULL'''.format(self.db_name, self.db_table_name)
        self._exec(query)
        self.commit()

    def fetch_recent_unverified_revs(self, num_revs: int):
        """
        fetch recent unverified revisions (i.e. revisions without labels) from training_revisions table

        param num_revs: number of revisions to fetch

        return list of revisions
        """

        query = """SELECT `id`, `wiki_id`, `page_id`, `page_title`, `parent_id`, `content`, `timestamp`,
                   `user_id`, `score` FROM `{0}`.`{1}` 
                   WHERE `good_editing` IS NULL ORDER BY timestamp DESC LIMIT {2}""".format(self.db_name, self.db_table_name, num_revs)
        return self._fetchall(query, as_dict=True)

    def fetch_unverified_revs(self, old_days: int):
        """
        fetch unverified revisions (i.e. revisions without labels) from training_revisions table

        param old_days: filter for fetch just revisions that older than this number of days relative to current date

        return list of tuples (wiki_id, page_id)
        """

        query = """SELECT `wiki_id`, `page_id` FROM `{0}`.`{1}` 
                    WHERE `good_editing` IS NULL AND `trained` = 0 
                    AND `timestamp` < NOW() - INTERVAL {2} DAY""".format(self.db_name, self.db_table_name, old_days)
        return self._fetchall(query)  # TODO: fetch as dict

    def update_good_revs(self, revs_wiki_ids: List[int], good_editing: bool):
        """
        update revisions labels (good or bad)

        param revs_wiki_ids: list of revisions Wikimedia ids

        param good_editing: if True - revision is good. otherwise, revision is bad
        """

        if not revs_wiki_ids:
            return
        place_holders = WikishieldDB.create_placeholders(len(revs_wiki_ids))
        query = '''UPDATE `{0}`.`{1}` SET
                `good_editing` = %s
                WHERE `wiki_id` IN ({2})'''.format(self.db_name, self.db_table_name, place_holders)
        args = (good_editing, *revs_wiki_ids)
        self._exec(query, args)

    def fetch_training_set(self, limit: int = None):
        """
        fetch training set

        param limit: limit data - the number of revisions. if limit None the function fetch all revisions from dataset.
        
        this function fetch list of revisions content and good_editing when content = X_text and good_editing = y

        return list of tuples of (content, good_editing)
        """

        query = '''SELECT `content`, `good_editing` FROM `{0}`.`{1}` 
                WHERE `good_editing` IS NOT NULL AND `trained` = 0'''.format(self.db_name, self.db_table_name)
        if limit is not None:
            query += " LIMIT {}".format(limit)
        return self._fetchall(query)

    def fetch_all_revs(self, fields: List[str] = ['id']):
        """
        fetch all revisions

        param fields: list of fields names to fetch

        return list of tuples with revisions fields values
        """

        if not fields:
            raise ValueError("Must be one field to fetch at least")

        fields_str = ", ".join(map(lambda f: "`" + f + "`", fields))

        query = "SELECT {0} FROM `{1}`.`{2}`".format(fields_str, self.db_name, self.db_table_name)
        return self._fetchall(query)

    def update_revs_contents(self):
        """
        update contents of all revisions

        this function re-extract words for all revisions using 'diff' field
        """

        revs = self.fetch_all_revs(fields=["id", "diff"])
        for rev_id, diff in revs:
            content = extract_added_words(self.lang, diff)
            self.update_rev_content(rev_id, content)
        self.commit()

    def update_rev_content(self, rev_id: int, content: str = ""):
        """
        update revision content

        param rev_id: the revision id for target revision

        param content: the new content for the revision
        """

        query = '''UPDATE `{0}`.`{1}` SET
                  `content` = %s
                   WHERE `id` = %s'''.format(self.db_name, self.db_table_name)
        args = (content, rev_id)
        self._exec(query, args)

    def update_rev_good_editing(self, rev_id: int, good_editing: bool):
        """
        update revision good editing

        param rev_id: the revision id for target revision

        param good_editing: if revision is good or not
        """

        query = '''UPDATE `{0}`.`{1}` SET
                  `good_editing` = %s
                   WHERE `id` = %s'''.format(self.db_name, self.db_table_name)
        args = (good_editing, rev_id)
        self._exec(query, args)

    def update_rev_score(self, rev_id: int, score: float):
        """
        update revision score

        param rev_id: the revision id for target revision

        param score: the score result
        """

        query = '''UPDATE `{0}`.`{1}` SET
                  `score` = %s
                   WHERE `id` = %s'''.format(self.db_name, self.db_table_name)
        args = (score, rev_id)
        self._exec(query, args)

    def update_revs_scores(self, revs: List):
        """
        update revisions scores

        param revs: list of revisions with ther scores to update
        """

        for rev in revs:
            self.update_rev_score(rev['id'], rev['score'])
        self.commit()

    def fetch_rev(self, rev_id: int):
        """
        fetch revision by id

        param rev_id: revision id

        return revision.
        """

        query = "SELECT * FROM `{0}`.`{1}` WHERE `id` = %s LIMIT 1".format(self.db_name, self.db_table_name)
        args = (rev_id,)
        revs = self._fetchall(query, args, as_dict=True)
        if not revs:
            raise ValueError("Cannot found revision with id = {}".format(rev_id))
        return revs[0]

    def fetch_page_id(self):
        """
        fetch page id from training revision table

        return tuples with page id fields values
        """

        query = "SELECT page_id FROM `{0}`.`{1}` WHERE page_title is null".format(self.db_name, self.db_table_name)
        return self._fetchall(query)

    def update_rev_page_title(self, page_id: int, page_title: str):
        """
        update page title in revision table

        param page_id: page id

        param page_title: string of title of the page
        """

        query = '''UPDATE `{0}`.`{1}` 
                    SET `page_title` = "{2}"
                    WHERE `page_id` = {3}
                  '''.format(self.db_name, self.db_table_name, page_title, page_id)
        print(query)
        self._exec(query)

    def update_rev_page_title_without_quotation(self, page_id: int, page_title: str):
        """
        note: the different from function above is the quotation mark inside the query to avoid bags

        update page title in revision table

        param page_id: page id

        param page_title: string of title of the page
        """

        query = '''UPDATE `{0}`.`{1}` 
                    SET `page_title` = '{2}'
                    WHERE `page_id` = {3}
                  '''.format(self.db_name, self.db_table_name, page_title, page_id)
        print(query)
        self._exec(query)

    def insert_rev(self, rev, diff_text: str, content: str):
        """
        insert a revision to `training_revisions` table

        if revision already exist (i.e. the revision have a same `wiki_id` field) it's not inserted to table

        param rev: revision

        param diff_text: the HTML different string of revision

        param content: the content that extracted from `diff_text`
        """

        args = (rev['wiki_id'], rev['page_id'], rev['page_title'], rev['parent_id'],
                BaseDB.clone_timestamp_cell(rev['timestamp']), int(rev['user_id']),
                diff_text, content, rev['score'])
        query = '''INSERT IGNORE INTO `{0}`.`{1}`
                (`wiki_id`, `page_id`, `page_title`, `parent_id`, `timestamp`, `user_id`, `diff`, `content`, `score`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''.format(self.db_name, self.db_table_name)
        self._exec(query, args=args)
