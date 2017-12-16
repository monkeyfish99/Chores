"""Chores app main page

Has database functions, app setup, and config loading."""

from flask import Flask, g
from flask_bcrypt import Bcrypt
from chores.blueprints.main_pages import MAIN_PAGES
from chores.blueprints.user import USER
import chores.blueprints.database as DATABASE


APPLICATION = Flask(__name__)
APPLICATION.register_blueprint(MAIN_PAGES)
APPLICATION.register_blueprint(USER)

BCRYPT = Bcrypt(APPLICATION)
APPLICATION.config.from_object(__name__)

with open("secret_key.txt") as f:
  SECRET = f.read()

APPLICATION.config.update(dict(
    SECRET_KEY=SECRET
))
APPLICATION.config.from_envvar("chores_settings", silent=True)

def initdb():
  """Read schema and start database with that

  Args: None

  Returns: None."""
  database = DATABASE.get_db()
  with APPLICATION.open_resource("schema.sql", mode="r") as file:
    database.cursor().executescript(file.read())
  database.commit()

@APPLICATION.cli.command("initdb")
def init_db_command():
  """Sets command for initdb, creates root user

  Args: None

  Returns: None."""
  initdb()
  print("Installed the database")

  data = DATABASE.get_db()
  hashed = BCRYPT.generate_password_hash("password")
  insert = ["root", True, hashed, True, "[]"]
  data.execute(
      "insert into users (username, admin, hash, root, assignable) values (?, ?, ?, ?, ?)",
      insert
      )
  data.commit()
  print("root user added, default password of 'password'")
  print("Please change this as soon as possible!")


@APPLICATION.teardown_appcontext
def close_db(none):
  """Closes database on app teartown

  Args: None

  Returns: None."""
  _ = none
  if hasattr(g, "sqlite_db"):
    g.sqlite_db.close()
