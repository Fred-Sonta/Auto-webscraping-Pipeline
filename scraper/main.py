import logging
from scraper.spiders.offres_spider import scrapper_offres_direct
from scraper.cleaners.cleaner import clean_and_load_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("=== Lancement manuel du pipeline WeWorkRemotely ===")
    scrapper_offres_direct(limite=50)
    clean_and_load_data()
    logging.info("=== Terminé ===")

if __name__ == "__main__":
    main()

    