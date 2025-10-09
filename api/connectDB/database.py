from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ========================
# CONFIG POSTGRESQL LOCAL
# ========================
DB_USER = "postgres"
DB_PASSWORD = "931752"  # ⚠️ à adapter
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "DB_MGPF"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ========================
# INITIALISATION SQLALCHEMY
# ========================
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def create_tables_if_not_exist():
    """
    ⚠️ Désactivé : tu gères manuellement la création/modification des tables.
    """
    print("ℹ️ Mode manuel activé : aucune création automatique de tables.")
