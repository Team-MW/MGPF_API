from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from api.connectDB.database import Base

# ========================================
# TABLE : PARKINGS
# ========================================
class Parking(Base):
    __tablename__ = "parkings"
    __table_args__ = {'autoload_with': None, 'extend_existing': True}  # lecture seule, pas de recréation

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    adresse = Column(String, nullable=True)
    admin_id = Column(Integer, nullable=True)

    # Relation 1:N avec les plaques
    plaques = relationship("Plaque", back_populates="parking")


# ========================================
# TABLE : PLAQUES
# ========================================
class Plaque(Base):
    __tablename__ = "plaques"
    __table_args__ = {'autoload_with': None, 'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=False, index=True)
    proprietaire = Column(String, nullable=False)
    entreprise = Column(String, nullable=True)
    place_numero = Column(String, nullable=True)
    parking_id = Column(Integer, ForeignKey("parkings.id"))
    date_enregistrement = Column(DateTime, default=datetime.utcnow)

    # Relation inverse vers Parking
    parking = relationship("Parking", back_populates="plaques")
