from seleniumbase import Driver
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cloudflare_seleniumbase():
    url_cible = "https://www.emploi.ci/recherche-jobs-cote-ivoire"
    logger.info("Initialisation de SeleniumBase en UC Mode...")
    
    # Lancement du driver en UC Mode (Undetected)
    # On garde headless=False pour l'instant afin de voir visuellement si on passe Cloudflare
    driver = Driver(uc=True, headless=False)
    
    try:
        logger.info(f"Navigation vers {url_cible}...")
        
        # uc_open_with_reconnect est la méthode magique de SeleniumBase pour Cloudflare
        # Elle ouvre la page, attend, et se reconnecte si le WAF tente de bloquer la session
        driver.uc_open_with_reconnect(url_cible, reconnect_time=6)
        
        # On attend que la page charge complètement ses éléments
        time.sleep(5)
        
        titre_page = driver.title
        logger.info(f"Titre de la page obtenu : {titre_page}")
        
        if "Attention Required!" in titre_page or "Just a moment..." in titre_page:
            logger.error("ÉCHEC : Cloudflare bloque toujours.")
        else:
            logger.info("SUCCÈS : Accès autorisé à Emploi.ci !")
            
            # Sauvegarde du code source pour vérifier la présence des données
            with open("scraper/raw_data/test_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info("Code source sauvegardé dans scraper/raw_data/test_page.html")

    except Exception as e:
        logger.error(f"Erreur : {e}")
        
    finally:
        logger.info("Fermeture du navigateur.")
        driver.quit()

if __name__ == "__main__":
    test_cloudflare_seleniumbase()

    