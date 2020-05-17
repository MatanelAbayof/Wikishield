import os

import pickle

import numpy as np
from pymysql.connections import Connection
from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from db.wikishield_db import WikishieldDB
from lang.langs import Lang
from db.connection_info import read_sql_user_name


class WikiClassifier:
    """
    this is a classifier class for learn and classified the dataset
    """
    PICKLE_FOLDER_PATH = r"assets/clfs"

    def __init__(self, lang: Lang, ctx: Connection = None):
        """
        initialize

        param lang: language

        param ctx: database context
        """

        self.lang = lang
        self.ctx = ctx
        self.vectorizer = None # type is TfidfVectorizer
        self.classifier = None # type is SVC

    def learn(self, limit: int = None):
        """
        partition to train set and test

        convert revs to token counts by using CountVectorizer

        fit calssifier on the train set

        param limit: limit data - the number of revisions. if limit None the function fetch all revisions from dataset.
        """

        sql_user_name = read_sql_user_name()
        wikishield_db = WikishieldDB(self.ctx, self.lang, sql_user_name)
        revs = wikishield_db.fetch_training_set(limit)

        X_text = np.asarray([rev[0] for rev in revs], dtype=object)
        y = np.asarray([rev[1] for rev in revs])

        self.vectorizer = HashingVectorizer(token_pattern=self.lang.extract_words_regex, decode_error='ignore',
                                            n_features=2 ** 18, alternate_sign=False)

        X_train_text, _, y_train, _ = train_test_split(X_text, y, test_size=0.2, random_state=0, shuffle=True)
        X_train = self.vectorizer.fit_transform(X_train_text)

        self.classifier = SVC(probability=True)

        self.classifier.fit(X_train, y_train)

    def score_rev(self, rev_text: str):
        """
        score a revision 

        param rev_text: revision text

        return array with score result: [ Pr(bad|rev), Pr(good|rev) ]
        """

        new_rev_data = self.vectorizer.transform([rev_text])
        new_rev_pred = self.classifier.predict_proba(new_rev_data)[0]
        return new_rev_pred.tolist()

    def to_pickle(self):
        """
        convert object to pickled representation.

        note that `ctx` cannot be pickled because it's includes SSLSocket object

        return pickled representation
        """

        obj = {'lang': self.lang, 'vectorizer': self.vectorizer, 'classifier': self.classifier}
        return pickle.dumps(obj)

    def pickle_to_file(self, file_path: str):
        """
        convert object to pickled representation and puts result in file

        note that `ctx` cannot be pickled because it's includes SSLSocket object

        param file_path: file path
        """

        obj = {'lang': self.lang, 'vectorizer': self.vectorizer, 'classifier': self.classifier}
        with open(file_path, 'wb') as pickle_file:
            pickle.dump(obj, pickle_file, protocol=2)

    @classmethod
    def from_pickle_file(cls, file_path: str):
        """
        convert classifier from pickled representation at file

        param file_path: pickle file path 

        return classifier
        """

        if not os.path.isfile(file_path):
            raise IOError("pickle file at '{}' don't exists".format(file_path))

        with open(file_path, "rb") as pickle_file:
            obj = pickle.load(pickle_file)
            clf = cls(obj['lang'])
            clf.vectorizer = obj['vectorizer']
            clf.classifier = obj['classifier']
            return clf

    @classmethod
    def from_pickle(cls, ctx: Connection, data: bytes):
        """
        convert classifier from pickled representation

        param ctx: connection context

        param data: pickled representation of classifier

        return classifier
        """

        obj = pickle.loads(data)
        clf = cls(obj['lang'], ctx)
        clf.vectorizer = obj['vectorizer']
        clf.classifier = obj['classifier']
        return clf
