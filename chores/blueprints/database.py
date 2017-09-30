'''Database functions

TODO(Connor): Even more database stuff.'''
import sqlite3
import os
from flask import g, Blueprint

DATABASE = Blueprint("database", __name__, template_folder="templates")

def connect_db():
  """Connect to the database file

  Args: None

  Returns: database info."""
  row = sqlite3.connect(os.path.join(DATABASE.root_path, "chores.db"))
  row.row_factory = sqlite3.Row
  return row

def get_db():
  """Fetches database for reading and writing

  Args: None

  Returns: database."""
  if not hasattr(g, "sqlite_db"):
    g.sqlite_db = connect_db()
  return g.sqlite_db
