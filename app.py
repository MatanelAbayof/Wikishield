import os
import sys

sys.path.append(os.getcwd())
from flask import Flask, render_template
from jobs.learn_clfs_job import LearnClfsJob
from routes.api import api
from routes.index import index
from clf.classifier_manager import reload_classifiers
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from lang.langs import Lang, LangsManager
from jobs.add_revs_job import AddRevsJob


directory = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, static_url_path='', static_folder=os.path.join(directory, 'public'), template_folder=os.path.join(directory, 'templates'))

#app.config["SERVER_NAME"] = ""
#app.config["APPLICATION_ROOT"] = ""


app.register_blueprint(index, url_prefix="/")
app.register_blueprint(api, url_prefix="/api")


# ----------------------------------------------------------------------------------------------------
@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# ----------------------------------------------------------------------------------------------------
def add_revs_job(lang: Lang):
    """
    start job that add revisions to database

    param lang: language
    """

    job = AddRevsJob(lang)
    job.start()


# ----------------------------------------------------------------------------------------------------
def learn_job():
    """
    start job that learn data for all classifiers
    """

    lcj = LearnClfsJob()
    lcj.start()

    # TODO: update **sync** clfs at app.config


# ----------------------------------------------------------------------------------------------------


scheduler = BackgroundScheduler()

lm = LangsManager()
for lang_name in lm.langs_names:
    lang = lm.get_lang(lang_name)
    add_revs_args = [lang]
    scheduler.add_job(func=add_revs_job, args=add_revs_args, trigger="interval",
                      seconds=300)  # 300 seconds = 5 minutes
scheduler.add_job(func=learn_job, trigger="interval", seconds=86400)  # 86400 seconds = a day
# TODO: add DB remover job
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

with app.app_context():
    # do this for learn
    app.config["classifiers"] = reload_classifiers()

# ----------------------------------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    """
    when page not found, this route raised
    """

    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


# ------------------------------------------ start server --------------------------------------------
if __name__ == '__main__':
    print("Running Wikishield server...")
    app.run(debug=False, use_reloader=False)
