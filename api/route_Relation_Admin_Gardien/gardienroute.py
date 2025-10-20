from flask import Blueprint, request, jsonify
import logging
from api.connectDB.database import get_db_connection

# === Création du Blueprint ===
gardien_bp = Blueprint('gardien', __name__)

# ========================================
# ROUTE : Enregistrement du suivi gardien
# ========================================
@gardien_bp.route('/suivi_gardien', methods=['POST'])
def suivi_gardien():
    """
    Reçoit les informations d'un scan du gardien et les stocke dans la table suivis_gardien.
    """
    try:
        data = request.get_json(force=True)
        plaque = data.get('plaque')
        statut = data.get('statut')
        type_scan = data.get('type_scan', 'auto')
        parking_id = data.get('parking_id')
        clerk_id = data.get('clerk_id')

        if not plaque or not statut:
            return jsonify({'success': False, 'message': 'Champs manquants'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO suivis_gardien (plaque, statut, parking_id, clerk_id, type_scan)
            VALUES (%s, %s, %s, %s, %s)
        """, (plaque, statut, parking_id, clerk_id, type_scan))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Suivi enregistré pour la plaque {plaque} ({statut})")
        return jsonify({'success': True, 'message': 'Suivi enregistré'}), 201

    except Exception as e:
        logging.error(f"Erreur suivi_gardien : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
