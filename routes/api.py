import json
from datetime import datetime, date

from flask import Blueprint, request
from flask import current_app as app

from db.wikishield_connection import DBConnection as WS
from db.wikishield_db import WikishieldDB
from lang.langs import Lang, LangsManager
from db.connection_info import read_sql_user_name

api = Blueprint('api', __name__)

