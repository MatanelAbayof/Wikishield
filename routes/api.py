import json
from datetime import datetime, date

from flask import Blueprint, request
from flask import current_app as app

from db.wikishield_connection import DBConnection as WS
from db.wikishield_db import WikishieldDB
from lang.langs import Lang, LangsManager
from db.connection_info import read_sql_user_name
from sklearn.exceptions import NotFittedError

api = Blueprint('api', __name__)

# TODO: close wikishield_db at all routes

# TODO: define HTTP status codes here

# ----------------------------------------------------------------------------------------------------
class WikishieldApiResult:
    """
    this class generate JSON results for Wikishield API
    """

    @staticmethod
    def build_good_res(data=None):
        """
        build good result JSON of API

        param data: data to send at response. data must be serializable value (i.e. can converted to dictionary).
                    if your data it numpy value. use `data = my_numpy_obj.item()` function for converting to pure Python object

        return JSON result
        """
        return json.dumps(obj={'status': 'ok', 'data': data}, default=WikishieldApiResult._encode_object)

    @staticmethod
    def build_err_res(err_msg: str = None):
        """
        build error result JSON of API

        param err_msg: error message

        return JSON result
        """

        return json.dumps(obj={'status': 'error', 'errInfo': {'errMsg': err_msg}},
                          default=WikishieldApiResult._encode_object)

    @staticmethod
    def _encode_object(obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, ValueError):
            return obj.__str__()  # return error message
        else:
            return obj.__dict__()

# ----------------------------------------------------------------------------------------------------
def _get_lang(lang_name: str):
    """
    get language from query parameters

    param lang_name: name of the language

    return language
    """

    lang_manager = LangsManager()
    if not lang_manager.is_support_lang(lang_name):
        raise ValueError("API not support `lang`={}".format(lang_name))
    return lang_manager.get_lang(lang_name)


# ----------------------------------------------------------------------------------------------------
def _try_parse_int(value: str):
    """
    try parse integer from string

    param value: string to parse

    return int
    """

    try:
        return int(value)
    except ValueError:
        raise ValueError("Cannot parse int from string")


# ----------------------------------------------------------------------------------------------------
def _try_parse_bool(value: str):
    """
    try parse boolean from string

    param value: string to parse

    return boolean
    """

    try:
        return bool(value)
    except ValueError:
        raise ValueError("Cannot parse boolean from string")


# ----------------------------------------------------------------------------------------------------
def _get_wikishield_db(lang: Lang):
    """
    get Wikishield database

    param lang: language

    return Wikishield database
    """


    sql_user_name = read_sql_user_name()
    wikishield_conn = WS(sql_user_name)
    wikishield_conn.start()
    return WikishieldDB(wikishield_conn.ctx, lang, sql_user_name)

# ----------------------------------------------------------------------------------------------------
@api.route('/score_rev', methods=['GET']) #TODO: change to POST
def score_rev():
    """
    score revision route

    request parameters:
                `rev_text` - revision text
                `lang` = language
    response:
                JSON with `scoreResult`
    """

    try:
        rev_text = request.args.get("rev_text")
        rev_text = rev_text.strip() if rev_text else False
        if not rev_text:
            return WikishieldApiResult.build_err_res("Missing `rev_text` parameter"), 400
        lang_name = request.args.get("lang")
        _get_lang(lang_name) # check language
        wiki_classifier = app.config["classifiers"][lang_name]
        score_result = wiki_classifier.score_rev(rev_text)
        return WikishieldApiResult.build_good_res({'scoreResult': score_result})
    except ValueError as err:
        err_msg = str(err)
        return WikishieldApiResult.build_err_res(err_msg), 400
    except Exception as ex: # TODO: use NotFittedError
        err_msg = str(ex)
        return WikishieldApiResult.build_err_res(err_msg), 400
    # TODO: handle another exceptions

# ----------------------------------------------------------------------------------------------------
@api.route('/manage_rev', methods=['POST'])
def manage_rev():
    """
    manage a revision at Wikipedia and update revision good editing in Wikishield table

    request parameters:
                `rev_id` - revision id to verify or restore
                `lang` = language
    response: /
    """

    try:
        req_data = request.get_json()
        rev_id = _try_parse_int(req_data['rev_id'])
        if rev_id < 1:
            raise ValueError("Parameter out of range `rev_id`={}".format(rev_id))
        lang_name = req_data['lang']
        lang = _get_lang(lang_name)
        good_editing = _try_parse_bool(req_data['good_editing'])
        wikishield_db = _get_wikishield_db(lang)
        wikishield_db.update_rev_good_editing(rev_id, good_editing)
        wikishield_db.commit()
        return WikishieldApiResult.build_good_res({})
    except ValueError as err:
        err_msg = str(err)
        return WikishieldApiResult.build_err_res(err_msg), 400
    # TODO: handle another exceptions

# ----------------------------------------------------------------------------------------------------
@api.route('/get_revs', methods=['GET'])
def get_revs():
    """
    get last unverified revisions

    request parameters:
                `num_revs` - number of revisions to fetch
                 `lang` = language
    response:
                JSON with list of revisions
    """
    try:
        num_revs = _try_parse_int(request.args.get("num_revs", default=50)) # TODO: use const
        if num_revs < 0 or num_revs > 500: # TODO: use const
            raise ValueError("Illegal parameter range `num_revs`")
        lang_name = request.args.get("lang")
        lang = _get_lang(lang_name)
        wikishield_db = _get_wikishield_db(lang)
        revs = wikishield_db.fetch_recent_unverified_revs(num_revs)
        return WikishieldApiResult.build_good_res({'revs': revs})
    except ValueError as err:
        err_msg = str(err)
        return WikishieldApiResult.build_err_res(err_msg), 400
    # TODO: handle another exceptions

# ----------------------------------------------------------------------------------------------------
@api.route('/<path:path>')
def unknown_request(path: str):
    """
    route for all unknown requests in API

    this return an error JSON response
    """

    err_msg = "Unknown request at path '{}'".format(path)
    return WikishieldApiResult.build_err_res(err_msg), 404
