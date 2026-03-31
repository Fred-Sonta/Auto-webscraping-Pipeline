import requests
from bs4 import BeautifulSoup
import json
import logging
import re

logger = logging.getLogger(__name__)

def scrapper_offres_direct(limite=500):
    url_cible = "https://weworkremotely.com/categories/all-other-remote-jobs"
    donnees_offres = []
    headers = {"User-Agent": "Mozilla/5.0 (ENSEA Educational Project - Observatoire Emploi Remote)"}

    logger.info(f"Début de l'extraction sur {url_cible}")

    try:
        response = requests.get(url_cible, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ciblage des balises <li> (en excluant les séparateurs)
        jobs = soup.select('section.jobs ul li:not(.view-all):not(.feature-breaker)')

        for job in jobs:
            if len(donnees_offres) >= limite:
                break

            # 1. URL et ID
            a_tag = job.find('a', class_='listing-link--unlocked')
            if not a_tag:
                # WWR a parfois des classes différentes pour les liens non sponsorisés
                a_tag = job.find('a', recursive=False) 
                if not a_tag: continue
            
            link = "https://weworkremotely.com" + a_tag.get('href', '')
            id_offre = link.split('-')[-1]

            # 2. Titre et Entreprise
            title_tag = job.select_one('.new-listing__header__title__text')
            title = title_tag.text.strip() if title_tag else "Non renseigné"
            
            company_tag = job.find('p', class_='new-listing__company-name')
            company = company_tag.text.strip() if company_tag else "Confidentiel"

            # 3. Extraction du Logo (Regex sur le background-image)
            logo_div = job.find('div', class_='tooltip--flag-logo__flag-logo')
            logo_url = ""
            if logo_div and 'style' in logo_div.attrs:
                match = re.search(r'url\((.*?)\)', logo_div['style'])
                if match:
                    logo_url = match.group(1)

            # 4. Tri intelligent des Catégories (Région, Salaire, Contrat, Tags)
            categories = job.find_all('p', class_='new-listing__categories__category')
            cat_texts = [c.text.strip() for c in categories if c.text.strip()]

            salaire = "Non renseigné"
            region = "Anywhere"
            type_contrat = "Non renseigné"
            tags = []

            for text in cat_texts:
                if '$' in text or '€' in text or '£' in text:
                    salaire = text
                elif text.lower() in ['full-time', 'contract', 'part-time', 'freelance']:
                    type_contrat = text
                elif 'anywhere' in text.lower() or 'only' in text.lower() or 'emea' in text.lower():
                    region = text
                else:
                    tags.append(text)

            # 5. Date
            date_span = job.select_one('.new-listing__header__icons__date span')
            date_pub = date_span.text.strip() if date_span else "Récent"

            donnees_offres.append({
                "id_externe": id_offre,
                "url": link,
                "titre_poste": title,
                "nom_entreprise": company,
                "region": region,
                "type_contrat": type_contrat,
                "salaire": salaire,
                "tags": ", ".join(tags) if tags else "Aucun",
                "logo_url": logo_url,
                "date_publication": date_pub
            })

    except Exception as e:
        logger.error(f"Erreur lors du scraping : {e}")

    with open('scraper/raw_data/donnees_brutes.json', 'w', encoding='utf-8') as f:
        json.dump(donnees_offres, f, ensure_ascii=False, indent=4)

    logger.info(f"Succès : {len(donnees_offres)} offres WWR extraites.")
    return donnees_offres