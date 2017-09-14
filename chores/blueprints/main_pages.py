from flask import Blueprint, render_template, abort

main_pages = Blueprint("main_pages", __name__, template_folder="templates")

@main_pages.route("/")
def index():
    return render_template("index.html", title="Home")