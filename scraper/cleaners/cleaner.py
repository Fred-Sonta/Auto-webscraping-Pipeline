import pandas as pd
import json
import logging
from db.database import SessionLocal, engine, Base
from db.models import Entreprise, Offre

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_and_load_data(filepath='scraper/raw_data/donnees_brutes.json'):
    Base.metadata.create_all(bind=engine)
    logger.info("Tables PostgreSQL vérifiées/créées.")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        logger.info(f"Fichier JSON chargé : {len(df)} lignes.")
        
        if df.empty:
            logger.warning("Le DataFrame est vide. Arrêt de l'ETL.")
            return
            
        # Mise à jour avec la nouvelle clé WWR
        df = df.drop_duplicates(subset=['id_externe'])
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df.fillna("Non renseigné", inplace=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement Pandas : {e}")
        return

    db = SessionLocal()
    try:
        entreprises_uniques = df['nom_entreprise'].unique()
        entreprise_id_map = {}
        
        for nom_ent in entreprises_uniques:
            ent_db = db.query(Entreprise).filter(Entreprise.nom == nom_ent).first()
            if not ent_db:
                ent_db = Entreprise(nom=nom_ent)
                db.add(ent_db)
                db.commit()
                db.refresh(ent_db)
            entreprise_id_map[nom_ent] = ent_db.id
            
        logger.info(f"{len(entreprises_uniques)} entreprises traitées/insérées.")

        offres_ajoutees = 0
        offres_ignorees = 0
        
        for _, row in df.iterrows():
            existe_deja = db.query(Offre).filter(Offre.id_externe == row['id_externe']).first()
            
            if not existe_deja:
                nouvelle_offre = Offre(
                    id_externe=row['id_externe'],
                    url=row['url'],
                    titre_poste=row['titre_poste'],
                    entreprise_id=entreprise_id_map[row['nom_entreprise']],
                    region=row['region'],
                    type_contrat=row['type_contrat'],
                    salaire=row['salaire'],
                    tags=row['tags'],
                    logo_url=row['logo_url'],
                    date_publication=row['date_publication']
                )
                db.add(nouvelle_offre)
                offres_ajoutees += 1
            else:
                offres_ignorees += 1
                
        db.commit()
        logger.info(f"Insertion terminée : {offres_ajoutees} nouvelles offres, {offres_ignorees} ignorées.")

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'insertion en base de données : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_load_data()

    