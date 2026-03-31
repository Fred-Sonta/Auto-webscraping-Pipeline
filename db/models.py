from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Entreprise(Base):
    __tablename__ = "entreprises"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True, nullable=False)
    offres = relationship("Offre", back_populates="entreprise")

class Offre(Base):
    __tablename__ = "offres"
    id = Column(Integer, primary_key=True, index=True)
    id_externe = Column(String, unique=True, index=True, nullable=False) # Renommé pour plus de cohérence
    url = Column(String, nullable=False)
    titre_poste = Column(String, nullable=False)
    
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)
    entreprise = relationship("Entreprise", back_populates="offres")

    region = Column(String) # Remplace "ville"
    type_contrat = Column(String)
    salaire = Column(String) # Nouvelle colonne
    tags = Column(String) # Nouvelle colonne (Featured, Top 100...)
    logo_url = Column(String) # Nouvelle colonne
    date_publication = Column(String)
    
    date_creation_db = Column(DateTime(timezone=True), server_default=func.now())

    