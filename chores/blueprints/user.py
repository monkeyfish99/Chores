'''User management

User admin page, user edit page, adding/removing users, logging in/out

TODO(Connor): Improve remove user double check.'''

from flask import Flask, Blueprint, render_template, \
  abort, session, request, redirect, url_for
from flask_bcrypt import Bcrypt
import chores.blueprints.database as DATABASE

USER = Blueprint("user", __name__, template_folder="templates")

APP = Flask(__name__)
BCRYPT = Bcrypt(APP)

@USER.route("/admin")
def show_admin():
  '''Show admin page if logged in and admin

  Renders admin.html template file, passes userlist to it.'''
  if not session.get("logged_in") or not session.get("admin"):
    abort(401)
  data = DATABASE.get_db()
  cur = data.execute("SELECT username, admin, root FROM users ORDER BY id")
  userlist = cur.fetchall()
  return render_template("admin.html", title="Admin Panel", users=userlist)

@USER.route("/adduser", methods=["POST"])
def add_user():
  '''Add user function

  Args (over POST):
    str: password
    str: confirm
    bool: admin
    str: username

  Redirects to the show_admin page.'''
  if not session.get("logged_in") and not session.get("admin"):
    abort(401)

  if request.form["password"] != request.form["confirm"]:
    return redirect(url_for("user.show_admin"))

  data = DATABASE.get_db()
  hashed = BCRYPT.generate_password_hash(request.form["password"])
  admin = bool(request.form.getlist("check"))

  insert = [request.form["username"].lower(), admin, hashed, False]
  data.execute("INSERT INTO users (username, admin, hash, root) VALUES (?, ?, ?, ?)", insert)
  data.commit()
  return redirect(url_for("user.show_admin"))

@USER.route("/login", methods=["GET", "POST"])
def login():
  '''User login page and function

  Args (over POST):
    str: username
    str: password

  If successful POST, redirect to DATABASE page.
  If failure POST, redirect to same page

  If over GET, display login page.'''
  error = None
  if request.method == "POST":
    data = DATABASE.get_db()
    cur = data.execute("SELECT username, hash, admin, root FROM users WHERE username = '%s'" % request.form["username"].lower())

    users = cur.fetchall()
    if not users:
      error = "Invalid username or password!"
      return render_template("login.html", error=error)

    user_list = users[0]

    if not BCRYPT.check_password_hash(user_list[1], request.form["password"]):
      error = "Invalid username or password!"
    else:
      session["logged_in"] = True
      session["username"] = request.form["username"].lower()

      session["admin"] = bool(user_list[2] == 1)
      session["root"] = bool(user_list[3] == 1)

      return redirect(url_for("main_pages.index"))
  return render_template("login.html", error=error, title="Login")

@USER.route("/logout")
def logout():
  '''Logs out the user
  Removes session["logged_in"] and session["admin"]

  Redirects to DATABASE page.'''
  session.pop("logged_in", None)
  session.pop("admin", None)
  return redirect(url_for("main_pages.index"))

@USER.route("/user/<username>")
def user_page(username):
  '''Displays user edit page.

  Only allow current logged in user to view their page if not admin
  If admin, show any user pages.

  Pass user admin flag to user.html template to render.'''
  if not session["logged_in"]:
    abort(401)
  if not session["admin"] and username != session["username"]:
    abort(401)

  data = DATABASE.get_db()
  admin_check = data.execute("SELECT admin FROM users WHERE username = '%s'" % username).fetchall()[0][0]
  return render_template("user.html", title="Edit "+username, user=username, admin=admin_check)

@USER.route("/user/<username>/edit", methods=["POST"])
def edit_user(username):
  '''Edit user information from user_page

  Args:
    str: password
    str: confirm
    bool: admin

  Set password and/or set admin flag on user
  Only allow admin flag change if logged in user is admin.'''
  if not session["logged_in"]:
    abort(401)
  if not session["admin"] and username != session["username"]:
    abort(401)

  if request.form["password"] != request.form["confirm"]:
    return redirect(url_for("user.user_page", username=username))

  data = DATABASE.get_db()
  root = data.execute("SELECT root FROM users WHERE username = '%s'" % username).fetchall()[0][0]
  if request.form["password"] and request.form["confirm"]:
    if request.form["password"] == request.form["confirm"]:
      hashed = BCRYPT.generate_password_hash(request.form["password"])
      data.execute("UPDATE users SET hash = ? WHERE username = '%s'" % username, [hashed])

  if session["admin"] or root == 1:
    if request.form.getlist("check") or root == 1:
      data.execute("UPDATE users SET admin = 1 WHERE username = '%s'" % username)
    else:
      data.execute("UPDATE users SET admin = 0 WHERE username = '%s'" % username)

  data.commit()
  return redirect(url_for("user.user_page", username=username))

@USER.route("/user/<username>/delete")
def delete_user(username):
  '''Asks for confirmation then deletes user

  Display a simple page for a confirm, with a bool in the URL for confirm

  Args (over GET):
    bool: confirm

  If confirmed, delete user from DATABASE.'''
  if not session["logged_in"] and not session["admin"]:
    abort(401)

  if request.args.get("confirm") == "False":
    return "Are you sure you want to delete user " + username + "? <a href=" + url_for("user.delete_user", username=username, confirm=True) + ">Yes</a>, <a href=" + url_for("user.show_admin") + ">No</a>"
  elif request.args.get("confirm") == "True":
    data = DATABASE.get_db()
    check = data.execute("SELECT root FROM users WHERE username = '%s'" % username)
    root = check.fetchall()
    if root[0][0] == 1:
      data.commit()
      return redirect(url_for("user.show_admin"))

    data.execute("DELETE FROM users WHERE username = '%s'" % username)
    data.commit()
    return redirect(url_for("user.show_admin"))
    