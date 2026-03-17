from seleniumbase import Driver
import logging

logger = logging.getLogger(__name__)

def get_stealth_browser(headless=False):
    """
    Initialise le navigateur en UC Mode pour contourner les WAF.
    Pour la phase de test, garde headless=False.
    """
    logger.info("Lancement du navigateur furtif (SeleniumBase)...")
    try:
        # L'option uc=True active l'undetected-chromedriver
        driver = Driver(uc=True, headless=headless)
        return driver
    except Exception as e:
        logger.error(f"Erreur fatale lors du lancement du navigateur : {e}")
        return None


        