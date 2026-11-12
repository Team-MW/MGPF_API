from api.connectDB.database import get_db_connection
from flask import Blueprint, request, jsonify
import psycopg2, logging, requests

# ==============================
# BLUEPRINT
# ==============================
create_account_bp = Blueprint('create_account_bp', __name__)

# ==============================
import os
CLERK_API_KEY = os.getenv("CLERK_API_KEY")  # défini dans api/.env
CLERK_API_URL = "https://api.clerk.com/v1/users"

# ==============================
# CONNEXION BASE DE DONNÉES
# ==============================

# ==============================
# ROUTE : CRÉATION D’UN GARDIEN
# ==============================
@create_account_bp.route('/admin/create_gardien', methods=['POST'])
def create_gardien():
    """
    Création d’un gardien depuis le tableau admin :
    - Vérifie si l’admin a bien un parking dans la table parking_id
    - Crée un compte Clerk pour le gardien
    - Lie ce gardien à ce parking dans droits_gardiens
    """
    try:
        data = request.get_json(force=True)
        admin_clerk_id = data.get('admin_clerk_id')
        gardien_email = data.get('email')

        if not admin_clerk_id or not gardien_email:
            return jsonify({'success': False, 'message': 'admin_clerk_id ou email manquant'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Étape 1️⃣ : récupérer le parking_id de l’admin
        cur.execute("SELECT id FROM parking_id WHERE admin_id = %s;", (admin_clerk_id,))
        row = cur.fetchone()

        if not row:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': (
                    "Aucun parking trouvé pour cet admin. "
                    "Veuillez d’abord créer un parking dans la table 'parking_id' "
                    "avant d’ajouter un gardien."
                )
            }), 404

        parking_id = row[0]

        # Étape 2️⃣ : création du gardien via l’API Clerk
        headers = {
            "Authorization": f"Bearer {CLERK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email_address": [gardien_email],  # 👈 mettre entre crochets = liste
            "skip_password_creation": True,
            "public_metadata": {
                "role": "gardien",
                "parking_id": parking_id
            }
        }

        response = requests.post(CLERK_API_URL, headers=headers, json=payload)

        if response.status_code not in [200, 201]:
            logging.error(f"❌ Erreur Clerk: {response.text}")
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': f"Erreur Clerk: {response.text}"}), 500

        clerk_user = response.json()
        gardien_clerk_id = clerk_user.get("id")

        # Étape 3️⃣ : enregistrement du lien dans la base
        cur.execute("""
            INSERT INTO droits_gardiens (clerk_id, parking_id, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (clerk_id)
            DO UPDATE SET parking_id = EXCLUDED.parking_id;
        """, (gardien_clerk_id, parking_id, 'gardien'))

        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"✅ Gardien {gardien_email} créé avec succès pour le parking {parking_id}")
        return jsonify({
            'success': True,
            'message': f"Gardien créé avec succès pour le parking {parking_id}",
            'gardien_clerk_id': gardien_clerk_id
        }), 201

    except Exception as e:
        logging.error(f"Erreur create_gardien : {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
