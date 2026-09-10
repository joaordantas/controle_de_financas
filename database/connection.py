import sqlite3
import os
import tempfile

LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage', 'banco.db')
DEFAULT_DB_PATH = (
    os.path.join(tempfile.gettempdir(), 'controle_financas_preview.db')
    if os.environ.get('VERCEL')
    else LOCAL_DB_PATH
)
DB_PATH = os.environ.get('FINANCE_DB_PATH', DEFAULT_DB_PATH)

def get_connection():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
