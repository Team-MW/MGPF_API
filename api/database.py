import sqlite3
from api.config import DATABASE_PATH

def get_info_by_plaque(numero):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT proprietaire, vehicule, statut FROM plaques WHERE numero = ?", (numero,))
    result = cursor.fetchone()
    conn.close()
    return result
