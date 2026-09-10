import sqlite3
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage', 'banco.db')
DB_PATH = os.environ.get('FINANCE_DB_PATH', DEFAULT_DB_PATH)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
