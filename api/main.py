import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import json
from api.connectDB.database import SessionLocal  # uniquement, pas create_tables_if_not_exist

from api.parking.parking_routes import parking_bp


# ========================================
# CONFIGURATION DES CHEMINS
# ========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ========================================
# IMPORTS INTERNES AVEC GESTION DE FALLBACK
# ========================================
try:
    from api.connectDB.database import create_tables_if_not_exist, SessionLocal
    from api.connectDB.models import Plaque, Parking
    from api.services.plaque_service import verifier_plaque
    from api.ocr_engine import extract_text
    from api.route_super_admin.rootSuperAdmin import super_admin_bp
    from api.route_Relation_Admin_Gardien.gardienroute import gardien_bp
    from api.route_Relation_Visiteur_Admin.routesVisiteur import routes_visiteur_bp
except ImportError:
    from connectDB.database import create_tables_if_not_exist, SessionLocal
    from connectDB.models import Plaque, Parking
    from services.plaque_service import verifier_plaque
    from ocr_engine import extract_text
    from route_super_admin.rootSuperAdmin import super_admin_bp
    from route_Relation_Admin_Gardien.gardienroute import gardien_bp
    from route_Relation_Visiteur_Admin.routesVisiteur import routes_visiteur_bp

# ========================================
# CONFIGURATION FLASK
# ========================================
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# ========================================
# ENREGISTREMENT DES BLUEPRINTS
# ========================================
app.register_blueprint(super_admin_bp)
app.register_blueprint(gardien_bp)
app.register_blueprint(routes_visiteur_bp)



app.register_blueprint(parking_bp)

# ========================================
# CONNEXION BASE DE DONNÉES
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
# ROUTE OCR - TEST PLAQUE PAR LE GARDIEN (améliorée + complète)
# ========================================
@app.route('/ocr', methods=['POST'])
def ocr():
    """
    Vérifie si une plaque est autorisée :
    - si 'text' est envoyé → saisie manuelle
    - si 'image' est envoyé → OCR automatique
    - Vérifie aussi dans la table 'demandes' si le statut est 'Refusée' → non autorisée
    - Filtrée selon le parking du gardien (droits_gardiens)
    """
    try:
        plaque_text = None
        clerk_id = request.form.get('clerk_id') or request.args.get('clerk_id')

        if not clerk_id:
            return jsonify({'text': '', 'statut': 'Erreur', 'message': 'clerk_id manquant'}), 400

        # === Connexion base ===
        conn = get_db_connection()
        cur = conn.cursor()

        # Étape 0 — Trouver le parking associé à ce gardien
        cur.execute("SELECT parking_id FROM droits_gardiens WHERE clerk_id = %s;", (clerk_id,))
        gardien_data = cur.fetchone()

        if not gardien_data:
            cur.close()
            conn.close()
            return jsonify({
                'text': '',
                'statut': 'Erreur',
                'message': f"Aucun parking associé au gardien ({clerk_id})."
            }), 403

        parking_id = gardien_data[0]

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
            cur.close()
            conn.close()
            return jsonify({'text': '', 'statut': 'Erreur', 'message': 'Aucune donnée reçue'}), 400

        if not plaque_text:
            cur.close()
            conn.close()
            return jsonify({'text': '', 'statut': 'Erreur', 'message': 'Plaque vide ou non lisible'}), 400

        # === Étape 1 : Vérifier dans la table 'demandes' (dernière entrée) ===
        cur.execute("""
            SELECT statut FROM demandes 
            WHERE plaque = %s AND parking_id = %s
            ORDER BY id DESC LIMIT 1;
        """, (plaque_text, parking_id))
        demande = cur.fetchone()

        if demande:
            statut_demande = demande[0]
            if statut_demande and statut_demande.lower() in ['refusée', 'refusee']:
                logging.info(f"❌ Plaque {plaque_text} refusée par le super admin (parking {parking_id})")
                cur.close()
                conn.close()
                return jsonify({
                    'text': plaque_text,
                    'statut': 'Non autorisé',
                    'message': f"La plaque {plaque_text} a été refusée par l'administration."
                }), 403

        # === Étape 2 : Vérifier dans la table 'parking' (pour CE parking uniquement) ===
        cur.execute("""
            SELECT proprietaire, entreprise, places_selectionnees, date_enregistrement
            FROM parking
            WHERE UPPER(plaque) = %s AND parking_id = %s
        """, (plaque_text, parking_id))

        result = cur.fetchone()
        cur.close()
        conn.close()

        # === Si plaque trouvée ===
        if result:
            proprietaire, entreprise, places, date_enreg = result
            logging.info(f"✅ Plaque autorisée : {plaque_text} (parking {parking_id})")
            return jsonify({
                'text': plaque_text,
                'statut': 'Autorisé',
                'proprietaire': proprietaire,
                'entreprise': entreprise,
                'places': places,
                'parking_id': parking_id,
                'date_enregistrement': str(date_enreg)
            }), 200

        # === Si plaque non trouvée ===
        else:
            logging.info(f"❌ Plaque inconnue : {plaque_text} (parking {parking_id})")
            return jsonify({
                'text': plaque_text,
                'statut': 'Non autorisé',
                'parking_id': parking_id,
                'message': f"La plaque {plaque_text} n'est pas enregistrée dans ce parking."
            }), 404

    except Exception as e:
        logging.error(f"Erreur OCR : {e}", exc_info=True)
        return jsonify({
            'text': '',
            'statut': 'Erreur',
            'message': str(e)
        }), 500



# ========================================
# ROUTE D'ENREGISTREMENT DE PLAQUE (corrigée)
# ========================================
@app.route('/register', methods=['POST'])
def register_plate():
    try:
        data = request.get_json(force=True)
        plaque = data.get('plate', '').strip().upper()
        proprietaire = data.get('owner', '').strip()
        entreprise = data.get('company', '').strip()
        places = data.get('parkingPlaces', [])  # liste ex: ["A1","A2"]
        admin_id = data.get('admin_id', 'inconnu')
        parking_id = data.get('parking_id')      # ✅ récupère l’ID du parking

        if not plaque or not proprietaire or not parking_id:
            return jsonify({'success': False, 'message': 'Champs requis manquants (plaque, owner, parking_id)'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # 💾 Insertion dans la table parking avec le parking_id
        cur.execute("""
            INSERT INTO parking (plaque, proprietaire, entreprise, places_selectionnees, admin_id, parking_id, date_enregistrement)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            plaque,
            proprietaire,
            entreprise,
            json.dumps(places),  # ✅ on stocke proprement en JSON
            admin_id,
            int(parking_id),
            datetime.now()
        ))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Plaque {plaque} enregistrée pour {proprietaire} (parking_id={parking_id})")
        return jsonify({'success': True, 'message': 'Plaque enregistrée avec succès'}), 201

    except Exception as e:
        logging.error(f"Erreur lors de l'enregistrement de la plaque : {e}", exc_info=True)
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
