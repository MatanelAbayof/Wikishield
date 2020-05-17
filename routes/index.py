from flask import Blueprint, redirect, render_template

index = Blueprint('index', __name__)


# ----------------------------------------------------------------------------------------------------
@index.route('/')
def homepage():
    """
    homepage route
    """

    return render_template("homepage.html")


# ----------------------------------------------------------------------------------------------------
@index.route('/score_rev')
def score_rev():
    """
    score revision route
    """

    return render_template("score_rev.html")


# ----------------------------------------------------------------------------------------------------
@index.route('/verify_revs')
def verify_revs():
    """
    verify revisions route
    """

    return render_template("verify_revs.html")


# ----------------------------------------------------------------------------------------------------
@index.route('/favicon.ico')
def favicon():
    """
    route of favorite icon

    the browser request this URL automatically
    """

    return redirect("images/logo.ico")
