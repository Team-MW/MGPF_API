import os

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Charge api/.env (non versionné, voir api/.env.example)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# ========================
# CONFIG POSTGRESQL (via .env)
# ========================
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "DB_MGPF")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_db_connection():
    """
    Fournit une connexion directe à PostgreSQL (hors SQLAlchemy)
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


# ========================
# INITIALISATION SQLALCHEMY
# ========================
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "false").lower() == "true")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def create_tables_if_not_exist():
    """
    ⚠️ Désactivé : tu gères manuellement la création/modification des tables.
    """
    print("ℹ️ Mode manuel activé : aucune création automatique de tables.")
