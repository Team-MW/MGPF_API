import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from api.connectDB.database import SessionLocal  # ✅ uniquement, pas create_tables_if_not_exist

# ========== CONFIG IMPORTS ==========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Imports internes ---
try:
    from api.connectDB.database import create_tables_if_not_exist, SessionLocal
    from api.connectDB.models import Plaque, Parking
    from api.services.plaque_service import verifier_plaque
    from api.ocr_engine import extract_text
    from api.super_admin.rootSuperAdmin import super_admin_bp  # 🟢 Import du blueprint
except ImportError:
    from connectDB.database import create_tables_if_not_exist, SessionLocal
    from connectDB.models import Plaque, Parking
    from services.plaque_service import verifier_plaque
    from ocr_engine import extract_text
    from super_admin.rootSuperAdmin import super_admin_bp  # 🟢 Import du blueprint

# ========================================
# CONFIGURATION DE FLASK
# ========================================
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)



# 🟢 ENREGISTREMENT DU BLUEPRINT SUPER ADMIN
app.register_blueprint(super_admin_bp)
# ========================================
# CONNEXION À LA BASE DE DONNÉES
# ========================================
def get_db_connection():
    return psycopg2.connect(
        dbname="DB_MGPF",
        user="postgres",
        password="931752",
        host="localhost",
        port="5432"
    )

# ========================================
# ROUTE OCR - TEST PLAQUE PAR LE GARDIEN
# ========================================
@app.route('/ocr', methods=['POST'])
def ocr():
    """
    Vérifie si une plaque est autorisée :
    - si 'text' est envoyé → saisie manuelle
    - si 'image' est envoyé → OCR automatique
    """
    try:
        plaque_text = None

        # === Cas 1 : Plaque saisie manuellement ===
        if 'text' in request.form:
            plaque_text = request.form['text'].strip().upper()
            logging.info(f"Plaque reçue manuellement : {plaque_text}")

        # === Cas 2 : Image envoyée pour OCR ===
        elif 'image' in request.files:
            image_file = request.files['image']
            image_bytes = image_file.read()
            from ocr_engine import extract_text
            plaque_text = extract_text(image_bytes).strip().upper()
            logging.info(f"Texte extrait via OCR : {plaque_text}")

        else:
            return jsonify({'text': '', 'statut': 'Erreur', 'message': 'Aucune donnée reçue'}), 400

        if not plaque_text:
            return jsonify({'text': '', 'statut': 'Erreur', 'message': 'Plaque vide ou non lisible'}), 400

        # === Vérification dans la base PostgreSQL ===
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT proprietaire, entreprise, places_selectionnees, date_enregistrement
            FROM parking
            WHERE plaque = %s
        """, (plaque_text,))

        result = cur.fetchone()
        cur.close()
        conn.close()

        # === Si plaque trouvée ===
        if result:
            proprietaire, entreprise, places, date_enreg = result
            logging.info(f"✅ Plaque autorisée : {plaque_text}")
            return jsonify({
                'text': plaque_text,  # ✅ attendu par le front
                'statut': 'Autorisé',
                'proprietaire': proprietaire,
                'entreprise': entreprise,
                'places': places,
                'date_enregistrement': str(date_enreg)
            }), 200

        # === Si plaque non trouvée ===
        else:
            logging.info(f"❌ Plaque inconnue : {plaque_text}")
            return jsonify({
                'text': plaque_text,  # ✅ pour affichage front
                'statut': 'Non autorisé',
                'message': f"La plaque {plaque_text} n'est pas enregistrée dans ce parking."
            }), 404

    except Exception as e:
        logging.error(f"Erreur OCR : {e}", exc_info=True)
        return jsonify({'text': '', 'statut': 'Erreur', 'message': str(e)}), 500

# ========================================
# ROUTE D'ENREGISTREMENT DE PLAQUE
# ========================================
@app.route('/register', methods=['POST'])
def register_plate():
    try:
        data = request.get_json(force=True)
        plaque = data.get('plate', '').strip().upper()
        proprietaire = data.get('owner', '').strip()
        entreprise = data.get('company', '').strip()
        places = data.get('parkingPlaces', [])
        admin_id = data.get('admin_id', 'inconnu')

        if not plaque or not proprietaire:
            return jsonify({'success': False, 'message': 'Champs requis manquants'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO parking (plaque, proprietaire, entreprise, places_selectionnees, admin_id, date_enregistrement)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (plaque, proprietaire, entreprise, str(places), admin_id, datetime.now()))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Plaque {plaque} enregistrée pour {proprietaire}")
        return jsonify({'success': True, 'message': 'Plaque enregistrée avec succès'}), 201

    except Exception as e:
        logging.error(f"Erreur lors de l’enregistrement de la plaque : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

# ========================================
# ROUTE GET - LISTE DES PLAQUES (debug)
# ========================================
@app.route('/plaques', methods=['GET'])
def get_all_plaques():
    db = SessionLocal()
    try:
        plaques = db.query(Plaque).all()
        result = [
            {
                'id': p.id,
                'numero': p.numero,
                'proprietaire': p.proprietaire,
                'entreprise': p.entreprise,
                'place_numero': p.place_numero,
                'parking_id': p.parking_id,
                'date_enregistrement': p.date_enregistrement.isoformat() if p.date_enregistrement else None
            }
            for p in plaques
        ]
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Erreur get_all_plaques : {e}", exc_info=True)
        return jsonify({'error': 'Erreur serveur'}), 500
    finally:
        db.close()

# ========================================
# ROUTE PAR DÉFAUT
# ========================================
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': '🚗 API Parking en ligne !'}), 200

# ========================================
# DÉMARRAGE DU SERVEUR
# ========================================
if __name__ == '__main__':
    app.run(debug=True, port=8090, use_reloader=False)
