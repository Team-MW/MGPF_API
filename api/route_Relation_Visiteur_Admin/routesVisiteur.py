import logging
from flask import Blueprint, request, jsonify
import psycopg2

# ==========================
# CONNEXION BASE DE DONNÉES
# ==========================
def get_db_connection():
    return psycopg2.connect(
        dbname="DB_MGPF",
        user="postgres",
        password="931752",
        host="localhost",
        port="5432"
    )

# ==========================
# BLUEPRINT VISITEUR
# ==========================
routes_visiteur_bp = Blueprint('routes_visiteur', __name__, url_prefix='/api')

# ==========================
# ROUTE : CRÉER UNE DEMANDE
# ==========================
@routes_visiteur_bp.route('/demandes', methods=['POST'])
def creer_demande():
    """
    Enregistre une nouvelle demande d’accès parking envoyée par un visiteur.
    Associe automatiquement la demande à l’admin du parking_id choisi.
    """
    try:
        data = request.get_json(force=True)
        parking_id = data.get('parking_id')
        plaque = data.get('plaque', '').strip().upper()
        entreprise = data.get('entreprise', '').strip()
        statut = data.get('statut', 'En attente')
        visiteur_id = data.get('visiteurId', None)
        email = data.get('email', None)

        if not parking_id or not plaque or not entreprise:
            return jsonify({'message': 'Champs requis manquants'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # 🔍 Trouver l’admin associé à ce parking_id
        cur.execute("SELECT admin_id FROM parking_id WHERE id = %s", (parking_id,))
        admin_result = cur.fetchone()

        if not admin_result:
            cur.close()
            conn.close()
            return jsonify({'message': f'Aucun administrateur trouvé pour le parking ID {parking_id}'}), 404

        admin_id = admin_result[0]

        # 💾 Enregistrer la demande
        cur.execute("""
            INSERT INTO demandes (parking_id, plaque, entreprise, statut, visiteur_id, email, admin_id, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (parking_id, plaque, entreprise, statut, visiteur_id, email, admin_id))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Nouvelle demande enregistrée pour parking_id {parking_id} - plaque {plaque}")
        return jsonify({'message': 'Demande enregistrée avec succès ✅'}), 201

    except Exception as e:
        logging.error(f"Erreur lors de la création de la demande : {e}", exc_info=True)
        return jsonify({'message': f'Erreur interne : {str(e)}'}), 500


# ==========================
# ROUTE : LISTE DES DEMANDES POUR L’ADMIN
# ==========================
@routes_visiteur_bp.route('/demandes', methods=['GET'])
def get_demandes():
    """
    Retourne la liste des demandes selon l’admin connecté.
    (via query param ?admin_id=...)
    """
    try:
        admin_id = request.args.get('admin_id')
        if not admin_id:
            return jsonify({'message': 'admin_id manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, parking_id, plaque, entreprise, statut, visiteur_id, email, date_creation
            FROM demandes
            WHERE admin_id = %s
            ORDER BY date_creation DESC
        """, (admin_id,))

        demandes = cur.fetchall()
        cur.close()
        conn.close()

        result = [
            {
                'id': d[0],
                'parking_id': d[1],
                'plaque': d[2],
                'entreprise': d[3],
                'statut': d[4],
                'visiteur_id': d[5],
                'email': d[6],
                'date_creation': d[7].isoformat() if d[7] else None
            }
            for d in demandes
        ]

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Erreur récupération demandes : {e}", exc_info=True)
        return jsonify({'message': f'Erreur interne : {str(e)}'}), 500
