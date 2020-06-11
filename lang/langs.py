import json
import logging


# ---------------------------------------------------------------------------------------------------------------
class Lang:
    """
    this class holds info of language
    """

    def __init__(self, lang_data):
        """
        initialize

        the data of any language holds in Json
        """

        self.name = lang_data["name"]
        self.language = lang_data["language"]
        self.undo_rev = lang_data["undo-rev"]
        self.extract_words_regex = lang_data["extract-words-regex"]
        self.extract_rev_regex = lang_data["extract-rev-regex"]

        # there is not filter for any language
        if "filter" in lang_data:
            self.filter = lang_data["filter"]
        else:
            self.filter = None


# ---------------------------------------------------------------------------------------------------------------
class LangsManager:
    """
    decode data from Json
    """
    LANGS_FILE_PATH = r"assets/langs.json"

    def __init__(self):
        """
        initialize
        """

        self._load_json()

    def _load_json(self):
        """
        load json from file
        """

        try:
            with open(self.LANGS_FILE_PATH, encoding='utf8') as json_file:
                self._data = json.load(json_file)["langs"]
        except:
            logging.exception("Cannot load '{0}' JSON file".format(self.LANGS_FILE_PATH))
            raise

    def print_data(self):
        """
        print data from json
        """

        print(self._data)

    def is_support_lang(self, lang: str):
        """
        check if the json file holds data of this language

        param lang: name of lnaguage

        return true/false
        """

        return lang in self.langs_names

    def get_lang(self, lang: str):
        """
        get specific lang from data

        param lang: name of lnaguage

        return Lang object
        """

        return Lang(next(lang_data for lang_data in self._data if lang_data["name"] == lang))

    @property
    def langs_names(self):
        """
        generator that yield list of languages names (ISO 639-1 codes)
        """

        for lang in self._data:
            yield lang["name"]
