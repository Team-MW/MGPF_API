from flask import Blueprint, request, jsonify
import uuid
import logging

admin_bp = Blueprint('admin_bp', __name__)

admins = []

@admin_bp.route("", methods=["GET"])
def get_admins():
    try:
        return jsonify(admins), 200
    except Exception as e:
        logging.error(f"Erreur get_admins : {e}", exc_info=True)
        return jsonify({'error': 'Erreur interne'}), 500


@admin_bp.route("", methods=["POST"])
def create_admin():
    try:
        data = request.get_json(force=True)
        new_admin = {
            "id": str(uuid.uuid4()),
            "fullName": data.get("fullName"),
            "email": data.get("email"),
            "role": data.get("role", "admin"),
            "createdAt": data.get("createdAt") or ""
        }
        admins.append(new_admin)
        logging.info(f"Nouvel admin créé : {new_admin['email']}")
        return jsonify(new_admin), 201
    except Exception as e:
        logging.error(f"Erreur create_admin : {e}", exc_info=True)
        return jsonify({'error': 'Erreur interne'}), 500


@admin_bp.route("/<admin_id>", methods=["PATCH"])
def update_admin(admin_id):
    try:
        data = request.get_json(force=True)
        for a in admins:
            if a["id"] == admin_id:
                a["role"] = data.get("role", a.get("role"))
                return jsonify({"message": "Rôle mis à jour"}), 200
        return jsonify({"error": "Admin non trouvé"}), 404
    except Exception as e:
        logging.error(f"Erreur update_admin : {e}", exc_info=True)
        return jsonify({'error': 'Erreur interne'}), 500


@admin_bp.route("/<admin_id>", methods=["DELETE"])
def delete_admin(admin_id):
    try:
        global admins
        before = len(admins)
        admins = [a for a in admins if a["id"] != admin_id]
        if len(admins) < before:
            return jsonify({"message": "Admin supprimé"}), 200
        else:
            return jsonify({"error": "Admin non trouvé"}), 404
    except Exception as e:
        logging.error(f"Erreur delete_admin : {e}", exc_info=True)
        return jsonify({'error': 'Erreur interne'}), 500
