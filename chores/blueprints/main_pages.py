'''Displays main pages

TODO(Connor): Add more pages to this, not just index.
TODO(Connor): Or migrate to chores.py.'''
from flask import Blueprint, render_template

MAIN_PAGES = Blueprint("main_pages", __name__, template_folder="templates")

@MAIN_PAGES.route("/")
def index():
  '''Displays index page.'''
  return render_template("index.html", title="Home")
