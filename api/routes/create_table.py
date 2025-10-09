from api.connectDB.database import Base, engine

print("🚀 Création des tables dans DB_MGPF...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès !")
