from pymysql.connections import Connection
from db.base_db import BaseDB
from lang.langs import Lang
from utils.algorithms import extract_rev_id
from typing import List


class WikimediaDB(BaseDB):
    """
    this class manage requests for Wikimedia database
    """

    def __init__(self, ctx: Connection, lang: Lang):
        """
        initialize Wikimedia database

        param ctx: connection context

        param lang: language
        """

        super().__init__(ctx, lang)

    @property
    def db_name(self):
        """
        return data base name
        """

        return self.lang.name + "wiki_p"  # 'p' for public

    def fetch_training_revs(self, num_of_revs: int, max_rev_id: int = None):
        """
        fetch revision from Wikimedia for dataset of Wikishield

        param num_of_revs: number of revision to fetch

        param max_rev_id: the maximum rev id number. for efficiency of query

        return array of revisions
        """

        max_rev_addition = " AND `rev_id` < {}".format(max_rev_id) if max_rev_id is not None else ""
        # Note: don't filter with timestamp because timestamp range is very slow query

        query = '''
                SELECT `r`.`rev_id` AS `wiki_id`, `r`.`rev_page` AS `page_id`, 
                       `r`.`rev_parent_id` AS `parent_id`, `r`.`rev_timestamp` AS `timestamp`, 
                       `r`.`rev_actor` AS `user_id`
                FROM `{0}`.`revision` AS `r`
                INNER JOIN `{0}`.`user_groups` AS `ug`
                ON `r`.`rev_actor` = `ug`.`ug_user`
                WHERE `r`.`rev_deleted` = 0 
                AND `r`.`rev_parent_id` <> 0 
                AND `ug`.`ug_group` NOT LIKE "bot"
                {1}
                GROUP BY `r`.`rev_id`
                ORDER BY `r`.`rev_id` DESC LIMIT %s
                '''.format(self.db_name, max_rev_addition)

        args = (num_of_revs,)
        return self._fetchall(query, args, as_dict=True)

    def filter_main_articles(self, revs: List):
        """
        filter revisions that are at main articles

        param revs: list of revisions to filter

        return filtered revisions
        """

        if not revs:
            return list()

        place_holders = WikimediaDB.create_placeholders(len(revs))

        query = '''
                SELECT `r`.`rev_id` AS `wiki_id` FROM `{0}`.`revision` AS `r`
                INNER JOIN `{0}`.`page` AS `p`
                ON `r`.`rev_page` = `p`.`page_id`
                WHERE `r`.`rev_id` IN ({1}) AND `p`.`page_namespace` = 0
                '''.format(self.db_name, place_holders)
        revs_ids = list(map(lambda row: row['wiki_id'], revs))
        args = tuple(revs_ids)
        filtered_revs_ids = list(map(lambda row: row['wiki_id'], self._fetchall(query, args, as_dict=True)))
        filtered_revs = list(filter(lambda rev: rev['wiki_id'] in filtered_revs_ids, revs))
        return filtered_revs

    def fetch_deleted_revs(self, revs_ids: List[int]):
        """
        fetch revision that deleted from wikimedia for dataset of wikishield

        param rev_ids: array of revisions ids

        return array of deleted_revisions
        """

        if not revs_ids:
            return list()
        place_holders = WikimediaDB.create_placeholders(len(revs_ids))
        query = '''
                SELECT * FROM `{0}`.`revision` AS `r`
                INNER JOIN `enwiki_p`.`comment_revision` AS `c`
                ON `r`.`rev_comment_id` = `c`.`comment_id`
                WHERE `rev_id` IN ({1})
                AND `r`.`rev_deleted` = 1
                '''.format(self.db_name, place_holders)
        args = tuple(revs_ids)
        return self._fetchall(query, args)

    def fetch_restored_rev(self, rev_id: int, rev_page: int):
        """
        fetch revision that restored because vandalism from wikimedia for dataset of wikishield

        param rev_id: single rev id

        param rev_id: single page id for efficiency of query

        param rev_page: revison page id

        return id of rev that restored
        """

        query = '''
                SELECT `r`.`rev_parent_id` FROM `{0}`.`revision` AS `r`
                INNER JOIN `{0}`.`comment_revision` AS `c`
                ON `r`.`rev_comment_id` = `c`.`comment_id`
                WHERE `r`.`rev_parent_id` = %s
                AND `r`.`rev_page` = %s
                AND `r`.`rev_id` > %s
                AND LOWER(`c`.`comment_text`) LIKE %s
                LIMIT 1
                '''.format(self.db_name)
        like_str = "%{}%".format(self.lang.undo_rev)
        args = (rev_id, rev_page, rev_id, like_str)
        return self._fetchall(query, args)

    def fetch_restored_revs(self, revs: List):
        """
        fetch revisions that restored because vandalism from Wikimedia for dataset of Wikishield

        param revs: array of revs id

        return list of ids of revs that restored
        """

        res = list()
        for idx, (rev_id, rev_page) in enumerate(revs):
            res.extend(self.fetch_restored_rev(rev_id, rev_page))
            print("finish fetch restored revision num {}".format(idx + 1))
        return res

    def fetch_bad_revs(self, size: int, max_comment_id: int = None):
        """
        fetch revision that restored because vandalism from Wikimedia for dataset of Wikishield

        param size: num of revision

        max_comment_id: max comment id of the part of fetch

        return tuple of bad revisions and minimum comment id
        """

        comments_result = self._fetch_restores_comments(size, max_comment_id)
        comments_ids = [c['id'] for c in comments_result]
        min_comment_id = min(comments_ids) if len(comments_ids) > 0 else None
        comments = [comment_res['text'].decode("utf-8") for comment_res in comments_result]
        revs_ids = [extract_rev_id(self.lang, comment) for comment in comments]
        revs_ids = list(filter(lambda x: x is not None, revs_ids))
        revs = self.fetch_revs(revs_ids)
        return revs, min_comment_id

    def _fetch_restores_comments(self, size: int, max_comment_id: int = None):
        """
        fetch comment ids of revs that restored because vandalism from wikimedia

        param size: num of revision

        max_comment_id: max comment id of the part of fetch for efficiency of query

        return array of comments
        """

        max_cmt_addition = " AND comment_id < {}".format(max_comment_id) if max_comment_id is not None else ""

        query = '''SELECT `comment_id` AS `id`, LOWER(`comment_text`) AS `text` FROM `{0}`.`comment_revision`
                   WHERE LOWER(`comment_text`) LIKE %s {1} 
                   ORDER BY `comment_id` DESC LIMIT {2}'''.format(self.db_name, max_cmt_addition, size)
        like_str = "%{}%".format(self.lang.undo_rev)
        args = (like_str,)
        return self._fetchall(query, args, as_dict=True)

    def fetch_revs(self, revs_ids: List[int]):
        """
        fetch list of revisions by revisions ids

        param revs_ids: list of revisions ids

        return list of revisions
        """

        if not revs_ids:
            return list()
        place_holders = WikimediaDB.create_placeholders(len(revs_ids))
        query = '''SELECT `rev_id` AS `wiki_id`, `rev_page` AS `page_id`, `rev_parent_id` AS `parent_id`, 
                   `rev_timestamp` AS `timestamp`, `rev_actor` AS `user_id`
                   FROM `{0}`.`revision` 
                   WHERE `rev_deleted` = 0 AND `rev_id` IN ({1})'''.format(self.db_name, place_holders)
        args = (revs_ids)
        return self._fetchall(query, args, as_dict=True)

    def fetch_natural_revs(self, lang: Lang, dataset_size: int, max_rev_id: int,
                           extra_part_size: int, min_part_size: int):
        """
        fetch natural revisions from Wikimedia database

        this function not fetch revisions contents (too big memory)

        param lang: language

        param wikimedia_db: Wikimedia database wrapper

        param wikishield_db: Wikishield database wrapper

        param wikimedia_api: Wikimedia API wrapper

        param dataset_size: the minimum size of dataset to fetch

        param max_rev_id: maximum revision id

        param extra_part_size: scalar for extra part size to fetch by the furmula: new_part_size = _EX_PART_SIZE*part_size

        param min_part_size: minimum part size to fetch, for effectively

        return pair of revisions and minimum revision id
        """

        wikimedia_training_set = []

        min_rev_id = max_rev_id

        while len(wikimedia_training_set) < dataset_size:

            part_size = extra_part_size * (dataset_size - len(wikimedia_training_set))
            if part_size < min_part_size:
                part_size = min_part_size
            part_train_set = self.fetch_training_revs(part_size, min_rev_id)
            part_revs_ids = [rev['wiki_id'] for rev in part_train_set]
            if len(part_revs_ids) > 0:
                min_rev_id = min(part_revs_ids)
            part_train_set = self.filter_main_articles(part_train_set)
            wikimedia_training_set += part_train_set

        print("finish fetch Wikimedia training set successfully")

        return wikimedia_training_set, min_rev_id

    def fetch_page_title(self, page_id: int):
        """
        fetch page title from page table of Wikimedia database

        param page_id: page id

        return tuple of title of the page
        """

        query = '''
                    SELECT page_title FROM {0}.page
                    WHERE page_id = {1}
                    LIMIT 1
                '''.format(self.db_name, page_id)
        print(query)
        return self._fetchall(query)
