import sqlite3
from api.config import DATABASE_PATH

def create_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plaques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            proprietaire TEXT,
            vehicule TEXT,
            statut TEXT
        )
    ''')
    conn.commit()
    conn.close()
