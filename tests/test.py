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
from db.wikishield_connection import DBConnection as WS
from db.connection_info import read_sql_user_name
sql_user_name = read_sql_user_name()
print('sql_user_name=', sql_user_name)
ws = WS(sql_user_name)
ws._connect()
with ws.ctx.cursor() as cur:
    cur.execute('SHOW TABLES')
    rows = cur.fetchall()
    print(rows)


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
