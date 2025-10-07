from flask import Blueprint, request, jsonify
import logging
import json

parking_bp = Blueprint('parking_bp', __name__)

#En attendant de faire une base de donnée
# Stockage temporaire en mémoire
parking_config = {
    'rows': 6,
    'cols': 6,
    'layout': [],
    'spots': []
}

@parking_bp.route('/config', methods=['POST'])

def save_parking_config():
    try:
        data = request.get_json(force=True)
        logging.info(">>> Données reçues du front :\n%s", json.dumps(data, indent=2))
        print(">>> Données reçues du front :")
        print(json.dumps(data, indent=2))  # Affiche joliment les données

        global parking_config
        parking_config = {
            'rows': data.get('rows'),
            'cols': data.get('cols'),
            'layout': data.get('layout', []),
            'spots': data.get('spots', [])
        }

        logging.info(f"Parking config sauvegardée : {parking_config['rows']}x{parking_config['cols']}")
        return jsonify({
            'success': True,
            'message': 'Configuration sauvegardée'
        }), 200


    except Exception as e:
        logging.error(f"Erreur save_parking_config : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@parking_bp.route('/config', methods=['GET'])
def get_parking_config():
    try:
        return jsonify({
            'success': True,
            'config': parking_config
        }), 200

    except Exception as e:
        logging.error(f"Erreur get_parking_config : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
