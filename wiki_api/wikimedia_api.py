import logging

from requests import ConnectionError

from lang.langs import Lang
from wiki_api.base_api import BaseApi


class WikimediaApi(BaseApi):
    """
    this class handle Wikimedia API functions
    """

    def __init__(self, lang: Lang):
        """
        initialize

        param lang: the language
        """

        self.lang = lang

    @property
    def api_path(self):
        """
        return the API URL path of Wikimedia of current language
        """

        return "https://{0}.wikipedia.org/w/api.php".format(self.lang.name)

    def send_req(self, params, ignore_err_codes=None):
        """
        send request with GET method to Wikimedia API

        param params: parameters/query of the URL

        return response as JSON or None when ignore error
        """

        if ignore_err_codes is None:
            ignore_err_codes = []
        try:
            response_json = self.fetch_json(params)  # TODO: add user agant & token of Wiki to request
            # check if was error in Wikimedia response
            if "error" in response_json:
                err_info = response_json["error"]
                err_code = err_info["code"]
                if err_code in ignore_err_codes:
                    return None
                raise ConnectionError("Wikimedia error: {0}".format(err_info))
            return response_json
        except:
            logging.exception("Cannot connect to Wikimedia API")
            raise

    def fetch_rev_diff(self, rev_id, parent_rev_id):
        """
        fetch revisions contents differents

        param rev_id: target revision id

        param parent_rev_id: source revision id

        return tuple of content differents and page title
        """

        req_params = {"action": "compare", "fromrev": parent_rev_id, "torev": rev_id,
                      "prop": "diff|diffsize|title", "format": "json"}

        ignore_err_codes = ["missingcontent", "nosuchrevid"]
        response_json = self.send_req(req_params, ignore_err_codes)

        if response_json is None:
            return None, None  # TODO: need return page title instead of None

        try:
            compare_res = response_json['compare']
            content = compare_res['*']
            page_title = compare_res['fromtitle']
            return content, page_title
        except:
            logging.exception("Cannot parse revision diff")
            raise
