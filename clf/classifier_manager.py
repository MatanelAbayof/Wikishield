from clf.wiki_classifier import WikiClassifier
from lang.langs import LangsManager


# ----------------------------------------------------------------------------------------------------
def reload_classifiers():
    """
    reload all classifiers from pickles files

    return directory of all classifiers by languages names
    """

    lm = LangsManager()
    return {lang_name: reload_classifier(lang_name) for lang_name in lm.langs_names}


# ----------------------------------------------------------------------------------------------------
def reload_classifier(lang_name: str):
    """
    reload a classifier from pickle file

    :param lang_name language name

    return classifier
    """

    file_path = WikiClassifier.PICKLE_FOLDER_PATH + '/' + lang_name + '.pickle'
    return WikiClassifier.from_pickle_file(file_path)
