import toolforge
import requests
import time

#toolforge.set_user_agent('wikishield')

import toolforge
args = {
    'host': 'tools.db.svc.eqiad.wmflabs'}
conn = toolforge.connect('s54207__wikishield_p', **args)







import pickle
file_path = r"assets/clfs/en.pickle"
with open(file_path, "rb") as pickle_file:
    obj2 = pickle.load(pickle_file)
    print(obj2)




# run test from venv
import sys
import os
wd = os.path.expanduser("~/www/python/src")
sys.path.append(wd)
os.chdir(wd)

from flask import Flask, render_template


from lang.langs import LangsManager, Lang
from jobs.add_revs_job import AddRevsJob
def add_revs_job(lang: Lang):
    print("add_revs_job")
    job = AddRevsJob(lang)
    job.start()

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
lm = LangsManager()
for lang_name in lm.langs_names:
    lang = lm.get_lang(lang_name)
    add_revs_args = [lang]
    scheduler.add_job(func=add_revs_job, args=add_revs_args, trigger="interval",
                      seconds=1)  # 300 seconds = 5 minutes
scheduler.start()
scheduler.print_jobs()


from lang.langs import LangsManager, Lang
lm = LangsManager()
lang = lm.get_lang('he')
from clf.wiki_classifier import WikiClassifier
file_path = WikiClassifier.PICKLE_FOLDER_PATH + '/' + lang.name + '.pickle'
wiki_classifier = WikiClassifier.from_pickle_file(file_path)
wiki_classifier.score_rev('גדגדג')


from jobs.learn_clfs_job import LearnClfsJob
lcb = LearnClfsJob()
lcb.start()

from lang.langs import LangsManager, Lang
lm = LangsManager()
lang = lm.get_lang('en')
from jobs.add_revs_job import AddRevsJob
arj = AddRevsJob(lang)
arj.start()

import app
app.app.run(debug=False, use_reloader=False)


from db.wikimedia_connection import DBConnection as WD
from db.connection_info import read_sql_user_name
sql_user_name = read_sql_user_name()
from lang.langs import LangsManager, Lang
lm = LangsManager()
lang = lm.get_lang('en')


import db.connections_manager as cm
ws, wd = cm.open_connections(lang)



from wiki_api.wikimedia_api import WikimediaApi
wapi = WikimediaApi(lang)
diff_text, page_title = wapi.fetch_rev_diff(324651969, 324548952)
print(diff_text)

from utils.algorithms import extract_added_words
extract_added_words(lang, diff_text)



wd = WD(sql_user_name, lang)
wd._connect()
from db.wikimedia_db import WikimediaDB
wdb = WikimediaDB(wd.ctx, lang)
revs = wdb.fetch_training_revs(10)
print(revs)

from clf.wiki_classifier import WikiClassifier
wc = WikiClassifier(lang, ws.ctx)
wc.learn(1000)
rev_text = 'Hello World'
wc.score_rev(rev_text)






from db.wikishield_connection import DBConnection as WS
ws = WS(sql_user_name)
ws._connect()
from db.wikishield_db import WikishieldDB
wsb = WikishieldDB(ws.ctx, lang, sql_user_name)
revs = wsb.fetch_training_set(300)
print(revs)

wsb.delete_empty_revs()




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
