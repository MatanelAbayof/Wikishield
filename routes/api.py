import json
from datetime import datetime, date

from flask import Blueprint, request
from flask import current_app as app

from db.wikishield_connection import DBConnection as WS
from db.wikishield_db import WikishieldDB
from lang.langs import Lang, LangsManager
from db.connection_info import read_sql_user_name

api = Blueprint('api', __name__)

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
        num_revs = _try_parse_int(request.args.get("num_revs", default=50))
        if num_revs < 0 or num_revs > 500:
            raise ValueError("Illegal parameter range `num_revs`")
        lang_name = request.args.get("lang")
        lang = _get_lang(lang_name)
        wikishield_db = _get_wikishield_db(lang)
        revs = wikishield_db.fetch_recent_unverified_revs(num_revs)
        return WikishieldApiResult.build_good_res({'revs': revs})
    except ValueError as err:
        err_msg = str(err)
        return WikishieldApiResult.build_err_res(err_msg), 400

# ----------------------------------------------------------------------------------------------------
@api.route('/<path:path>')
def unknown_request(path: str):
    """
    route for all unknown requests in API

    this return an error JSON response
    """

    err_msg = "Unknown request at path '{}'".format(path)
    return WikishieldApiResult.build_err_res(err_msg), 404
