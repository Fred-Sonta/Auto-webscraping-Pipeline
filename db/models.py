from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Entreprise(Base):
    __tablename__ = "entreprises"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True, nullable=False)
    
    # Relation : Une entreprise peut avoir plusieurs offres
    offres = relationship("Offre", back_populates="entreprise")

class Offre(Base):
    __tablename__ = "offres"

    id = Column(Integer, primary_key=True, index=True)
    id_emploi_ci = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    titre_poste = Column(String, nullable=False)
    
    # Clé étrangère vers la table entreprises
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)
    entreprise = relationship("Entreprise", back_populates="offres")

    ville = Column(String)
    type_contrat = Column(String)
    niveau_etude_requis = Column(String)
    experience_requise = Column(String)
    competences_cles = Column(Text)
    description_brute = Column(Text)
    date_publication = Column(String) # Gardé en String pour l'instant, formattage possible plus tard
    
    # Métadonnées d'insertion
    date_creation_db = Column(DateTime(timezone=True), server_default=func.now())