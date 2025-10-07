from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import logging
import uuid
import json

from ocr_engine import extract_text
from api.database import get_info_by_plaque
from api.modelsTeste import create_table

app = Flask(__name__)
CORS(app)
create_table()

logging.basicConfig(level=logging.INFO)


# ========================================
# ROUTE OCR - SCAN DE PLAQUE
# ========================================
@app.route('/ocr', methods=['POST'])
def ocr():
    """
    Route pour scanner une plaque d'immatriculation
    - Accepte une image (caméra) ou du texte (saisie manuelle)
    - Retourne le statut : Autorisé/Non autorisé
    """
    try:
        # Cas 1: Saisie manuelle de la plaque
        if 'text' in request.form:
            plaque_text = request.form['text'].replace(" ", "").upper()
            logging.info(f"Plaque reçue manuellement : {plaque_text}")

            info = get_info_by_plaque(plaque_text)
            if info:
                response = {
                    'text': plaque_text,
                    'statut': 'Autorisé',
                    'proprietaire': info[0]
                }
            else:
                response = {
                    'text': plaque_text,
                    'statut': 'Non autorisé',
                    'message': 'Plaque inconnue'
                }
            return jsonify(response), 200

        # Cas 2: Image de la caméra
        if 'image' not in request.files:
            logging.warning("Aucune image reçue")
            return jsonify({'error': 'Aucun fichier image reçu'}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()
        # image = Image.open(io.BytesIO(image_bytes))  # Si besoin de PIL

        # Extraction du texte via OCR
        informationOCR = extract_text(image_bytes).replace(" ", "").upper()
        logging.info(f"Texte extrait par OCR : {informationOCR}")

        # Vérification dans la base
        info = get_info_by_plaque(informationOCR)
        if info:
            response = {
                'text': informationOCR,
                'statut': 'Autorisé',
                'proprietaire': info[0]
            }
        else:
            response = {
                'text': informationOCR,
                'statut': 'Non autorisé',
                'message': 'Plaque inconnue'
            }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Erreur OCR : {e}", exc_info=True)
        return jsonify({'error': 'Erreur interne OCR'}), 500


# ========================================
# ROUTE D'ENREGISTREMENT DE PLAQUE
# ========================================
@app.route('/register', methods=['POST'])
def register_plate():
    """
    Route pour enregistrer une nouvelle plaque avec ses places de parking
    Reçoit: { plate, owner, company, parkingPlaces: ['A1', 'B2', ...] }
    """
    try:
        data = request.get_json(force=True)
        plate = data.get('plate', '').replace(" ", "").upper()
        owner = data.get('owner', '')
        company = data.get('company', '')
        parking_places = data.get('parkingPlaces', [])  # Liste des places attribuées

        if not plate or not owner:
            return jsonify({'success': False, 'message': 'Champs requis manquants'}), 400

        # Importe ta fonction d'insertion dans la base
        from api.database import insert_new_plate

        # Insertion de la plaque (adapter ta fonction pour inclure parking_places)
        success = insert_new_plate(plate, owner, company, parking_places)

        if success:
            logging.info(f"Plaque {plate} enregistrée pour {owner} - Places: {parking_places}")
            return jsonify({'success': True}), 201
        else:
            return jsonify({'success': False, 'message': 'Plaque déjà existante'}), 409

    except Exception as e:
        logging.error(f"Erreur register_plate : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ========================================
# POINT D'ENTRÉE
# ========================================
if __name__ == '__main__':
    app.run(debug=True, port=8090)