# api/parkings/parking_routes.py
from flask import Blueprint, jsonify, request
import psycopg2, json, logging
from datetime import datetime

parking_bp = Blueprint('parking_bp', __name__)

# ─────────────────────────────────────────────────────────────────────────────
# Connexion PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────
def get_db_connection():
    return psycopg2.connect(
        dbname="DB_MGPF",
        user="postgres",
        password="931752",
        host="localhost",
        port="5432"
    )

# ─────────────────────────────────────────────────────────────────────────────
# GET - Récupération configuration persistée du parking
# ─────────────────────────────────────────────────────────────────────────────
@parking_bp.route('/parking/config/<int:parking_id>', methods=['GET'])
def get_parking_config_db(parking_id):
    """
    Retourne la configuration complète d’un parking (grille, layout, spots).
    Si aucune configuration n’existe encore, renvoie une structure vide.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT rows, cols, layout, spots
            FROM parking_layouts
            WHERE parking_id = %s
        """, (parking_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            # Parking non configuré → valeurs par défaut
            return jsonify({
                'success': True,
                'config': {
                    'rows': 6,
                    'cols': 6,
                    'layout': [],
                    'spots': []
                }
            }), 200

        rows, cols, layout, spots = row

        # layout et spots peuvent être JSONB → s’assurer de retourner une liste Python
        layout = layout if isinstance(layout, list) else json.loads(layout)
        spots = spots if isinstance(spots, list) else json.loads(spots)

        return jsonify({
            'success': True,
            'config': {
                'rows': rows,
                'cols': cols,
                'layout': layout,
                'spots': spots
            }
        }), 200

    except Exception as e:
        logging.error(f"[get_parking_config_db] Erreur : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# POST/PUT - Sauvegarde ou mise à jour de la configuration
# ─────────────────────────────────────────────────────────────────────────────
@parking_bp.route('/parking/config/<int:parking_id>', methods=['POST', 'PUT'])
def save_parking_config_db(parking_id):
    """
    Sauvegarde la configuration (layout, spots, dimensions) d’un parking.
    Utilise UPSERT pour écraser la config précédente.
    """
    try:
        data = request.get_json(force=True)
        rows = int(data.get('rows', 6))
        cols = int(data.get('cols', 6))
        layout = data.get('layout', [])
        spots = data.get('spots', [])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO parking_layouts (parking_id, rows, cols, layout, spots, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (parking_id)
            DO UPDATE SET 
                rows = EXCLUDED.rows,
                cols = EXCLUDED.cols,
                layout = EXCLUDED.layout,
                spots = EXCLUDED.spots,
                updated_at = EXCLUDED.updated_at
        """, (parking_id, rows, cols, json.dumps(layout), json.dumps(spots), datetime.now()))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Configuration du parking {parking_id} sauvegardée ({rows}x{cols})")
        return jsonify({'success': True, 'message': 'Configuration sauvegardée avec succès'}), 200

    except Exception as e:
        logging.error(f"[save_parking_config_db] Erreur : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# PATCH - Met à jour rapidement l’état d’une place (occupée/libre)
# ─────────────────────────────────────────────────────────────────────────────
@parking_bp.route('/parking/occupancy/<int:parking_id>', methods=['PATCH'])
def patch_occupancy(parking_id):
    """
    Met à jour uniquement le statut d'une place (ex: A1 → 'occupied' ou 'free')
    sans modifier toute la configuration.
    """
    try:
        body = request.get_json(force=True)
        spot_id = body.get('spot_id')
        status = body.get('status')  # 'occupied' ou 'free'

        if not spot_id or status not in ('occupied', 'free'):
            return jsonify({'success': False, 'message': 'Données invalides'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Récupère les spots actuels
        cur.execute("SELECT spots FROM parking_layouts WHERE parking_id=%s", (parking_id,))
        row = cur.fetchone()
        current_spots = json.loads(row[0]) if row and row[0] else []

        # Met à jour le statut du spot
        found = False
        for s in current_spots:
            if s.get('id') == spot_id:
                s['status'] = status
                found = True
                break
        if not found:
            current_spots.append({'id': spot_id, 'status': status})

        # Sauvegarde
        cur.execute("""
            INSERT INTO parking_layouts (parking_id, rows, cols, layout, spots, updated_at)
            VALUES (%s, 6, 6, '[]', %s, NOW())
            ON CONFLICT (parking_id)
            DO UPDATE SET spots = EXCLUDED.spots, updated_at = NOW()
        """, (parking_id, json.dumps(current_spots)))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"🟢 Occupation mise à jour : {spot_id} = {status}")
        return jsonify({'success': True, 'spots': current_spots}), 200

    except Exception as e:
        logging.error(f"[patch_occupancy] Erreur : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# GET - Récupère toutes les places déjà occupées (depuis table parking)
# ─────────────────────────────────────────────────────────────────────────────
@parking_bp.route('/places_occupees/<int:parking_id>', methods=['GET'])
def get_places_occupees(parking_id):
    """
    Retourne la liste des places déjà utilisées dans le parking donné,
    à partir de la colonne 'places_selectionnees' de la table 'parking'.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT places_selectionnees
            FROM parking
            WHERE parking_id = %s
        """, (parking_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        occupied_places = []
        for row in rows:
            if not row or not row[0]:
                continue
            try:
                # Certaines sont stockées en JSON, d’autres en texte
                parsed = json.loads(row[0]) if isinstance(row[0], str) and row[0].startswith('[') else row[0].split(',')
                occupied_places.extend([p.strip() for p in parsed if p.strip()])
            except Exception:
                continue

        occupied_places = sorted(set(occupied_places))
        return jsonify({'success': True, 'places_occupees': occupied_places}), 200

    except Exception as e:
        logging.error(f"[get_places_occupees] Erreur : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
