# database_connection_h.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "tutorias_h.db")

def get_connection():
    """
    Devuelve una conexión SQLite con Row factory (dict-like).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
