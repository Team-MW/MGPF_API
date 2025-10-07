import sqlite3
from api.config import DATABASE_PATH

def insert_plaque(numero, proprietaire, vehicule, statut):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO plaques (numero, proprietaire, vehicule, statut)
        VALUES (?, ?, ?, ?)
    """, (numero, proprietaire, vehicule, statut))

    conn.commit()
    conn.close()
    print(f"✅ Plaque '{numero}' ajoutée avec statut : {statut}")

# Ajout de la plaque RDC pour SOFIAN
insert_plaque("RDC", "SOFIAN", "Accès autorisé", "Autorisé")
