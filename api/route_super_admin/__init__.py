from api.connectDB.database import get_db_connection
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
import psycopg2

# === Création du Blueprint (à importer dans main.py ensuite)
super_admin_bp = Blueprint('route_super_admin', __name__)

# === Connexion PostgreSQL

# ========================================
# 📘 ROUTE : RÉCUPÉRER TOUTES LES DEMANDES
# ========================================
@super_admin_bp.route('/api/demandes', methods=['GET'])
def get_demandes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM demandes ORDER BY id DESC;")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Erreur get_demandes : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# ✏️ ROUTE : MODIFIER LE STATUT D’UNE DEMANDE
# ========================================
@super_admin_bp.route('/api/demandes/<int:demande_id>', methods=['PATCH'])
def update_demande(demande_id):
    try:
        data = request.get_json()
        statut = data.get('statut')
        if not statut:
            return jsonify({'error': 'Statut manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE demandes SET statut = %s WHERE id = %s",
            (statut, demande_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Statut mis à jour'}), 200
    except Exception as e:
        logging.error(f"Erreur update_demande : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# 🗑️ ROUTE : SUPPRIMER UNE DEMANDE
# ========================================
@super_admin_bp.route('/api/demandes/<int:demande_id>', methods=['DELETE'])
def delete_demande(demande_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM demandes WHERE id = %s", (demande_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Demande supprimée'}), 200
    except Exception as e:
        logging.error(f"Erreur delete_demande : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# 👥 ROUTE : RÉCUPÉRER TOUS LES ADMINS
# ========================================
@super_admin_bp.route('/api/admins', methods=['GET'])
def get_admins():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admins ORDER BY id DESC;")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Erreur get_admins : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# ✏️ ROUTE : MODIFIER LE RÔLE D’UN ADMIN
# ========================================
@super_admin_bp.route('/api/admins/<int:admin_id>', methods=['PATCH'])
def update_admin_role(admin_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        if not new_role:
            return jsonify({'error': 'Rôle manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE admins SET role = %s WHERE id = %s",
            (new_role, admin_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Rôle mis à jour'}), 200
    except Exception as e:
        logging.error(f"Erreur update_admin_role : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# 🗑️ ROUTE : SUPPRIMER UN ADMIN
# ========================================
@super_admin_bp.route('/api/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Administrateur supprimé'}), 200
    except Exception as e:
        logging.error(f"Erreur delete_admin : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ========================================
# 🧾 ROUTE : VUE COMPLÈTE DU PARKING
# ========================================
@super_admin_bp.route('/api/parking', methods=['GET'])
def get_parking_data():
    """
    Retourne toutes les lignes de la table 'parking'
    pour affichage complet dans le dashboard SuperAdmin.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM parking ORDER BY id DESC;")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Erreur get_parking_data : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
