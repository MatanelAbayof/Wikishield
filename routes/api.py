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
@api.route('/<path:path>')
def unknown_request(path: str):
    """
    route for all unknown requests in API

    this return an error JSON response
    """

    err_msg = "Unknown request at path '{}'".format(path)
    return WikishieldApiResult.build_err_res(err_msg), 404
