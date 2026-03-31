from tasks.celery_app import celery_app
import logging
from scraper.spiders.offres_spider import scrapper_offres_direct
from scraper.cleaners.cleaner import clean_and_load_data

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="run_scraping_pipeline")
def run_scraping_pipeline(self):
    logger.info("=== DÉMARRAGE DU PIPELINE WWR (RAPIDE) ===")
    
    try:
        # Phase 1 : Extraction Ultra-Rapide (Requests)
        scrapper_offres_direct(limite=150)
        
        # Phase 2 : ETL (Pandas -> PostgreSQL)
        logger.info("Lancement du nettoyage et de l'insertion...")
        clean_and_load_data('scraper/raw_data/donnees_brutes.json')
        
        return {"status": "succès", "message": "Pipeline WWR exécuté complètement"}
    except Exception as e:
        logger.error(f"Erreur critique dans le pipeline : {e}")
        return {"status": "erreur", "message": str(e)}
    
    