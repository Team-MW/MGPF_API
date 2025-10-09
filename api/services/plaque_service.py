import logging
from api.connectDB.database import SessionLocal
from api.connectDB.models import Plaque

def verifier_plaque(plaque_text: str) -> dict:
    """
    Vérifie si une plaque est autorisée en base de données PostgreSQL.
    """
    db = SessionLocal()
    try:
        plaque = plaque_text.replace(" ", "").upper()
        logging.info(f"Vérification de la plaque : {plaque}")

        found = db.query(Plaque).filter(Plaque.numero == plaque).first()

        if found:
            logging.info(f"✅ Plaque autorisée : {plaque}")
            return {
                "text": plaque,
                "statut": "Autorisé",
                "proprietaire": found.proprietaire,
                "entreprise": found.entreprise,
            }
        else:
            logging.info(f"❌ Plaque non reconnue : {plaque}")
            return {
                "text": plaque,
                "statut": "Non autorisé",
                "message": "Plaque inconnue dans ce parking",
            }

    except Exception as e:
        logging.error(f"Erreur vérification plaque : {e}", exc_info=True)
        return {"text": plaque_text, "statut": "Erreur", "message": str(e)}
    finally:
        db.close()
