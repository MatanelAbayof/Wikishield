import os
import db.wikimedia_connection as wikimedia_conn
from db.wikimedia_connection import DBConnection as WD
import db.wikishield_connection as wikishield_conn
from db.wikishield_connection import DBConnection as WS
from pymysql.connections import Connection
from db.wikishield_db import WikishieldDB
from db.wikimedia_db import WikimediaDB
from wiki_api.wikimedia_api import WikimediaApi
from lang.langs import Lang
from db.connection_info import read_sql_user_name


# ----------------------------------------------------------------------------------------------------------
def open_connections(lang: Lang):
    """
    open databases connections

    param lang: language

    return tuple of and Wikishield connection and Wikimedia connection  
    """

    sql_user_name = read_sql_user_name()
    
    wd = WD(sql_user_name, lang)
    wd._connect()
    ws = WS(sql_user_name)
    ws._connect()
    return ws, wd


# -----------------------------------------------------------------------------------------------------------
def close_connections(ws_conn: WS, wd_conn: WD):
    """
    close databases connections

    param ws_conn: Wikishield database connection

    param wd_conn: Wikimedia database connection
    """

    ws_conn.close()
    wd_conn.close()


# -----------------------------------------------------------------------------------------------------------
def init_sources(source_ctx: Connection, dest_ctx: Connection, lang: Lang):
    """
    initialize sources wrappers

    param source_ctx: source context

    param source_ctx: destination context

    param lang: language

    return: tuple of (wikimedia_db, wikishield_db, wikimedia_api)
    """

    sql_user_name = read_sql_user_name()
    wikimedia_db = WikimediaDB(source_ctx, lang)
    wikishield_db = WikishieldDB(dest_ctx, lang, sql_user_name)
    wikimedia_api = WikimediaApi(lang)
    return wikimedia_db, wikishield_db, wikimedia_api
