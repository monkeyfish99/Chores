import os
import sqlite3
from flask import Flask, session, request, g, redirect, url_for, abort, render_template, flash
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(__name__)

with open("secret_key.txt") as f:
    secret = f.read()

app.config.update(dict(
    database = os.path.join(app.root_path, "chores.db"),
    SECRET_KEY = secret
))
app.config.from_envvar("chores_settings", silent=True)

def connect_DB():
    rv = sqlite3.connect(app.config["database"])
    rv.row_factory = sqlite3.Row
    return rv
    
def initDB():
    db = get_DB()
    with app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    
@app.cli.command("initdb")
def init_DB_command():
    initDB()
    print("Installed the database")
    
    db = get_DB()
    hash = bcrypt.generate_password_hash("password")
    db.execute("insert into users (username, admin, hash, root) values (?, ?, ?, ?)", ["root", True, hash, True])
    db.commit()
    print("root user added, default password of 'password'")
    print("Please change this as soon as possible!")
     
def get_DB():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_DB()
    return g.sqlite_db
    
@app.teardown_appcontext
def close_DB(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()
        
@app.route("/adduser", methods=["POST"])
def add_user():
    if not session.get("logged_in") and not session.get("admin"):
        abort(401)
    if request.form["password"] != request.form["confirm"]:
        return redirect(url_for("show_admin"))
    db = get_DB()
    hash = bcrypt.generate_password_hash(request.form["password"])
    if request.form.getlist("check"):
        admin = True
    else:
        admin = False
    db.execute("INSERT INTO users (username, admin, hash, root) VALUES (?, ?, ?, ?)", [request.form["username"].lower(), admin, hash, False])
    db.commit()
    flash("User has been added")
    return redirect(url_for("show_admin"))

@app.route("/admin")
def show_admin():
    if not session.get("logged_in") or not session.get("admin"):
        abort(401)
    db = get_DB()
    cur = db.execute("SELECT username, admin, root FROM users ORDER BY id")
    userlist = cur.fetchall()
    return render_template("admin.html", title="Admin Panel", users=userlist)
    
@app.route("/")
def index():
    return render_template("index.html", title="Home")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        db = get_DB()
        cur = db.execute("SELECT username, hash, admin, root FROM users WHERE username = '%s'" % request.form["username"].lower())

        users = cur.fetchall()
        if not users:
            error = "Invalid username or password!"
            return render_template("login.html", error=error)
            
        list = users[0]
        
        if not bcrypt.check_password_hash(list[1],request.form["password"]):
            error = "Invalid username or password!"
        else:
            session["logged_in"] = True
            session["username"] = request.form["username"].lower()
            if list[2] == 1:
                session["admin"] = True
            else:
                session["admin"] = False
                
            if list[3] == 1:
                session["root"] = True
            else:
                session["root"] = False
                
            flash("Logged in!")
            return redirect(url_for("index"))
    return render_template("login.html", error=error, title="Login")
    
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("admin", None)
    flash("You're now logged out")
    return redirect(url_for("index"))
    
@app.route("/user/<username>")
def user_page(username):
    if not session["logged_in"]:
        abort(401)
    if not session["admin"] and username != session["username"]:
        abort(401)
    
    db = get_DB()
    data = db.execute("SELECT admin FROM users WHERE username = '%s'" % username).fetchall()[0][0]
    return render_template("user.html", title="Edit "+username, user=username, admin=data)
    
@app.route("/user/<username>/edit", methods=["POST"])
def edit_user(username):
    if not session["logged_in"]:
        abort(401)
    if not session["admin"] and username != session["username"]:
        abort(401)
        
    if request.form["password"] != request.form["confirm"]:
        return redirect(url_for("user_page", username=username))    
    
    db = get_DB()
    root = db.execute("SELECT root FROM users WHERE username = '%s'" % username).fetchall()[0][0]
    hash = bcrypt.generate_password_hash(request.form["password"])
    if (request.form.getlist("check") and session["admin"]) or root == 1:
        admin = True
    else:
        admin = False
    db.execute("UPDATE users SET admin = ?, hash = ? WHERE username = '%s'" % username, [admin, hash])
    db.commit()
    flash("User has been added")
    return redirect(url_for("user_page", username=username))
        
@app.route("/user/<username>/delete")
def delete_user(username):
    if not session["logged_in"] and not session["admin"]:
        abort(401)
    if request.args.get("confirm") == "False":
        return "Are you sure you want to delete user " + username + "? <a href=" + url_for("delete_user", username=username,  confirm=True) + ">Yes</a>, <a href=" + url_for("show_admin") + ">No</a>"
    elif request.args.get("confirm") == "True":
        db = get_DB()
        check = db.execute("SELECT root FROM users WHERE username = '%s'" % username)
        root = check.fetchall()
        if root[0][0] == 1:
            db.commit()
            return redirect(url_for("show_admin"))
        db.execute("DELETE FROM users WHERE username = '%s'" % username)
        db.commit()
        return redirect(url_for("show_admin"))