import toolforge
import requests

#toolforge.set_user_agent('wikishield')

import toolforge
args = {
    'host': 'tools.db.svc.eqiad.wmflabs'}
conn = toolforge.connect('s54207__wikishield_p', **args)






# run test from venv
import sys
import os
wd = os.path.expanduser("~/www/python/src")
sys.path.append(wd)
os.chdir(wd)
from db.wikimedia_connection import DBConnection as WD
from db.connection_info import read_sql_user_name
sql_user_name = read_sql_user_name()
from lang.langs import LangsManager, Lang
lm = LangsManager()
lang = lm.get_lang('en')



wd = WD(sql_user_name, lang)
wd._connect()
from db.wikimedia_db import WikimediaDB
wdb = WikimediaDB(wd.ctx, lang)
revs = wdb.fetch_training_revs(10)
print(revs)






from db.wikishield_connection import DBConnection as WS
ws = WS(sql_user_name)
ws._connect()
from db.wikishield_db import WikishieldDB
wsb = WikishieldDB(ws.ctx, lang, sql_user_name)
revs = wsb.fetch_training_set()
print(revs)




from lang.langs import LangsManager, Lang
lm = LangsManager()
lang = lm.get_lang('en')
from db.wikimedia_connection import DBConnection as WD
wd = WD(sql_user_name, lang)
wd._connect()
with wd.ctx.cursor() as cur:
    cur.execute('SHOW TABLES')
    rows = cur.fetchall()
    print(rows)
