from clf.wiki_classifier import WikiClassifier
from lang.langs import LangsManager


# ----------------------------------------------------------------------------------------------------
def reload_classifiers():
    """
    reload all classifiers from pickles files

    return all classifiers
    """

    clfs = {}
    lm = LangsManager()
    for lang_name in lm.langs_names:
        file_path = WikiClassifier.PICKLE_FOLDER_PATH + '/' + lang_name + '.pickle'
        clf = WikiClassifier.from_pickle_file(file_path)
        clfs[lang_name] = clf
    return clfs

