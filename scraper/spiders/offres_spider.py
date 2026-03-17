import time
import json
import random
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def scrapper_offres_direct(driver, url_base, limite=150):
    donnees_offres = []
    page_actuelle = url_base

    logger.info(f"Début de l'extraction directe (Objectif : {limite} offres)")

    while page_actuelle and len(donnees_offres) < limite:
        try:
            logger.info(f"Scraping de la page : {page_actuelle}")
            driver.uc_open_with_reconnect(page_actuelle, reconnect_time=4)
            time.sleep(random.uniform(3, 5)) # Pause pour simuler un humain

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # Ciblage exact du bloc parent que tu as identifié
            cartes = soup.find_all('div', class_='card-job-detail')

            if not cartes:
                logger.warning("Aucune carte d'offre trouvée sur cette page.")
                break

            for card in cartes:
                if len(donnees_offres) >= limite:
                    break

                offre = {}

                # 1. Titre, ID et URL
                title_tag = card.find('h3')
                if title_tag and title_tag.find('a'):
                    a_tag = title_tag.find('a')
                    offre['titre_poste'] = a_tag.get_text(strip=True)
                    url_offre = a_tag.get('href', '')
                    # Reconstitution de l'URL absolue
                    offre['url'] = "https://www.emploi.ci" + url_offre if url_offre.startswith('/') else url_offre
                    offre['id_emploi_ci'] = url_offre.split('-')[-1].replace('.html', '')
                else:
                    continue # On ignore si la structure est anormale

                # 2. Entreprise
                company_tag = card.find('a', class_='company-name')
                offre['nom_entreprise'] = company_tag.get_text(strip=True) if company_tag else "Confidentiel"

                # 3. Initialisation des champs par défaut
                offre['niveau_etude_requis'] = "Non renseigné"
                offre['experience_requise'] = "Non renseigné"
                offre['type_contrat'] = "Non renseigné"
                offre['ville'] = "Non renseigné"
                offre['competences_cles'] = "Non renseigné"

                # 4. Extraction dynamique depuis les balises <li> et <strong>
                ul_tag = card.find('ul')
                if ul_tag:
                    for li in ul_tag.find_all('li'):
                        texte_li = li.get_text().lower()
                        strong_tag = li.find('strong')
                        # On prend le texte en gras s'il existe, sinon on nettoie la ligne
                        valeur = strong_tag.get_text(strip=True) if strong_tag else li.get_text(strip=True).split(':')[-1].strip()

                        if "études" in texte_li or "etude" in texte_li:
                            offre['niveau_etude_requis'] = valeur
                        elif "expérience" in texte_li or "experience" in texte_li:
                            offre['experience_requise'] = valeur
                        elif "contrat" in texte_li:
                            offre['type_contrat'] = valeur
                        elif "région" in texte_li or "region" in texte_li:
                            offre['ville'] = valeur
                        elif "compétences" in texte_li or "competence" in texte_li:
                            offre['competences_cles'] = valeur

                # 5. Description brute (le premier <p> dans la div de description)
                desc_tag = card.find('div', class_='card-job-description')
                if desc_tag:
                    p_tag = desc_tag.find('p')
                    offre['description_brute'] = p_tag.get_text(strip=True) if p_tag else desc_tag.get_text(strip=True)
                else:
                    offre['description_brute'] = "Non renseigné"

                # 6. Date de publication
                time_tag = card.find('time')
                offre['date_publication'] = time_tag.get('datetime', "Non renseigné") if time_tag else "Non renseigné"

                donnees_offres.append(offre)

            logger.info(f"Progression : {len(donnees_offres)}/{limite} offres extraites.")

            # Gestion de la pagination (Ciblage du bouton suivant)
            bouton_suivant = soup.find('li', class_='pagination-next')
            if bouton_suivant and bouton_suivant.find('a'):
                href = bouton_suivant.find('a').get('href')
                page_actuelle = href if href.startswith('http') else "https://www.emploi.ci" + href
            else:
                logger.info("Dernière page de pagination atteinte.")
                page_actuelle = None

        except Exception as e:
            logger.error(f"Erreur sur la page {page_actuelle} : {e}")
            break

    # Sauvegarde du JSON final
    with open('scraper/raw_data/donnees_brutes.json', 'w', encoding='utf-8') as f:
        json.dump(donnees_offres, f, ensure_ascii=False, indent=4)

    logger.info(f"Pipeline terminé. {len(donnees_offres)} offres ont été sauvegardées avec succès.")
    return donnees_offres

