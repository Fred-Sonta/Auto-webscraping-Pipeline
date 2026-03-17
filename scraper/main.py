import logging
import os
from scraper.driver.browser import get_stealth_browser
from scraper.spiders.offres_spider import scrapper_offres_direct

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    os.makedirs('scraper/raw_data', exist_ok=True)
    url_offres = "https://www.emploi.ci/recherche-jobs-cote-ivoire"
    
    driver = get_stealth_browser(headless=False)
    if not driver:
        return

    try:
        logger.info("=== DÉMARRAGE DU PIPELINE D'EXTRACTION ===")
        # L'objectif est fixé à 150 items
        scrapper_offres_direct(driver, url_offres, limite=150)
            
    finally:
        driver.quit()
        logger.info("Navigateur fermé.")

if __name__ == "__main__":
    main()

    