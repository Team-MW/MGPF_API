import logging
from flask import Blueprint, jsonify, request
import psycopg2
from datetime import datetime

# ============================
# CONFIGURATION DU BLUEPRINT
# ============================
super_admin_bp = Blueprint('route_super_admin', __name__)

# ============================
# CONNEXION À LA BASE
# ============================
def get_db_connection():
    return psycopg2.connect(
        dbname="DB_MGPF",
        user="postgres",
        password="931752",  # ⚠️ Mets ton mot de passe PostgreSQL ici
        host="localhost",
        port="5432"
    )


# ============================
#  ROUTE - LISTE DES DEMANDES pas fonctionnel
# ============================
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


# ============================
# ✏ MODIFIER UNE DEMANDE pas fonctionnel
# ============================
@super_admin_bp.route('/api/demandes/<int:demande_id>', methods=['PATCH'])
def update_demande(demande_id):
    try:
        data = request.get_json()
        statut = data.get('statut')
        if not statut:
            return jsonify({'error': 'Statut manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE demandes SET statut = %s WHERE id = %s", (statut, demande_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Statut mis à jour'}), 200
    except Exception as e:
        logging.error(f"Erreur update_demande : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ============================
# ️ SUPPRIMER UNE DEMANDE pas fonctionnel
# ============================
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


# ============================
#  LISTE DES ADMINS pas fonctionnel
# ============================
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


# ============================
#  MODIFIER RÔLE ADMIN pas fonctionnel
# ============================
@super_admin_bp.route('/api/admins/<int:admin_id>', methods=['PATCH'])
def update_admin_role(admin_id):
    try:
        data = request.get_json()
        role = data.get('role')
        if not role:
            return jsonify({'error': 'Rôle manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE admins SET role = %s WHERE id = %s", (role, admin_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Rôle mis à jour'}), 200
    except Exception as e:
        logging.error(f"Erreur update_admin_role : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ============================
#  SUPPRIMER ADMIN Pas fonctionel
# ============================
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


# ============================
#  VUE COMPLÈTE DU PARKING FONCTIONNEL
# ============================
@super_admin_bp.route('/api/parking', methods=['GET'])
def get_parking():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM parking ORDER BY id DESC;")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Erreur get_parking : {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==========================
# ➕ ROUTE — Créer un nouveau parking_id.   faut crée le front qui va avec
# ==========================
@super_admin_bp.route('/parking_id', methods=['POST'])
def create_parking_id():
    """
    Le Super Admin crée un nouveau parking_id pour un admin.
    Champs requis : nom, admin_id
    """
    try:
        data = request.get_json(force=True)
        nom = data.get('nom')
        admin_id = data.get('admin_id')

        if not nom or not admin_id:
            return jsonify({'message': 'Champs requis manquants (nom, admin_id)'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # 🔍 Vérifier si un parking existe déjà pour cet admin
        cur.execute("SELECT * FROM parking_id WHERE admin_id = %s", (admin_id,))
        existing = cur.fetchone()
        if existing:
            return jsonify({'message': 'Un parking est déjà associé à cet administrateur.'}), 400

        # 💾 Insertion
        cur.execute("INSERT INTO parking_id (nom, admin_id) VALUES (%s, %s) RETURNING id", (nom, admin_id))
        new_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Nouveau parking_id créé : {nom} (id={new_id})")
        return jsonify({
            'success': True,
            'message': 'Parking créé avec succès ✅',
            'parking_id': new_id
        }), 201

    except Exception as e:
        logging.error(f"Erreur lors de la création du parking : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================
# 📜 ROUTE — Liste des parkings existants
# ==========================
@super_admin_bp.route('/parking', methods=['GET'])
def get_parkings():
    """
    Retourne la liste de tous les parkings_id existants.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nom, admin_id FROM parking_id ORDER BY id ASC")
        parkings = cur.fetchall()

        result = [{'id': p[0], 'nom': p[1], 'admin_id': p[2]} for p in parkings]

        cur.close()
        conn.close()
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Erreur récupération parkings : {e}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@super_admin_bp.route('/parking_id/<int:parking_id>', methods=['DELETE'])
def delete_parking_id(parking_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM parking_id WHERE id = %s", (parking_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Parking supprimé avec succès ✅'}), 200
    except Exception as e:
        logging.error(f"Erreur delete_parking_id : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
