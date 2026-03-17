import pandas as pd
import json
import logging
from db.database import SessionLocal, engine, Base
from db.models import Entreprise, Offre

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_and_load_data(filepath='scraper/raw_data/donnees_brutes.json'):
    # 1. Création des tables dans PostgreSQL (si elles n'existent pas)
    Base.metadata.create_all(bind=engine)
    logger.info("Tables PostgreSQL vérifiées/créées.")

    # 2. Chargement et nettoyage avec Pandas
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        logger.info(f"Fichier JSON chargé : {len(df)} lignes.")
        
        # Suppression des doublons stricts basés sur l'ID du site
        df = df.drop_duplicates(subset=['id_emploi_ci'])
        
        # Nettoyage des espaces superflus
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Remplacement des valeurs vides par "Non renseigné"
        df.fillna("Non renseigné", inplace=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement Pandas : {e}")
        return

    # 3. Insertion dans la base de données
    db = SessionLocal()
    try:
        # A. Gestion du référentiel Entreprises
        entreprises_uniques = df['nom_entreprise'].unique()
        entreprise_id_map = {} # Dictionnaire pour stocker la correspondance Nom -> ID
        
        for nom_ent in entreprises_uniques:
            # Vérifier si l'entreprise existe déjà dans la DB
            ent_db = db.query(Entreprise).filter(Entreprise.nom == nom_ent).first()
            if not ent_db:
                ent_db = Entreprise(nom=nom_ent)
                db.add(ent_db)
                db.commit()
                db.refresh(ent_db)
            
            # On stocke l'ID pour l'associer aux offres ensuite
            entreprise_id_map[nom_ent] = ent_db.id
            
        logger.info(f"{len(entreprises_uniques)} entreprises traitées/insérées.")

        # B. Insertion des Offres
        offres_ajoutees = 0
        offres_ignorees = 0
        
        for _, row in df.iterrows():
            # Vérifier si l'offre existe déjà (pour éviter les doublons lors des futures exécutions Celery)
            existe_deja = db.query(Offre).filter(Offre.id_emploi_ci == row['id_emploi_ci']).first()
            
            if not existe_deja:
                nouvelle_offre = Offre(
                    id_emploi_ci=row['id_emploi_ci'],
                    url=row['url'],
                    titre_poste=row['titre_poste'],
                    entreprise_id=entreprise_id_map[row['nom_entreprise']],
                    ville=row['ville'],
                    type_contrat=row['type_contrat'],
                    niveau_etude_requis=row['niveau_etude_requis'],
                    experience_requise=row['experience_requise'],
                    competences_cles=row['competences_cles'],
                    description_brute=row['description_brute'],
                    date_publication=row['date_publication']
                )
                db.add(nouvelle_offre)
                offres_ajoutees += 1
            else:
                offres_ignorees += 1
                
        db.commit()
        logger.info(f"Insertion terminée : {offres_ajoutees} nouvelles offres, {offres_ignorees} ignorées (déjà existantes).")

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'insertion en base de données : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_load_data()

    