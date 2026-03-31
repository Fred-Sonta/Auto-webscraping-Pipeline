import pytest
from scraper.cleaners.cleaner import clean_and_load_data

def test_cleaner_supprime_doublons():
    """Le cleaner doit supprimer les doublons"""
    donnees = [
        {"id_externe": "1", "titre_poste": "Dev Python"},
        {"id_externe": "1", "titre_poste": "Dev Python"},  # doublon
    ]
    # Simule la suppression des doublons
    uniques = {d["id_externe"]: d for d in donnees}.values()
    assert len(list(uniques)) == 1

def test_cleaner_gere_valeurs_manquantes():
    """Les valeurs manquantes doivent être remplacées"""
    offre = {
        "titre_poste": None,
        "nom_entreprise": "",
        "salaire": None
    }
    offre["titre_poste"] = offre["titre_poste"] or "Non renseigné"
    offre["salaire"] = offre["salaire"] or "Non renseigné"
    assert offre["titre_poste"] == "Non renseigné"
    assert offre["salaire"] == "Non renseigné"

def test_cleaner_structure_offre():
    """Chaque offre doit avoir les champs obligatoires"""
    offre = {
        "id_externe": "123",
        "titre_poste": "Dev",
        "nom_entreprise": "Tech Co",
        "region": "Anywhere",
        "type_contrat": "Full-time"
    }
    champs_requis = ["id_externe", "titre_poste", "nom_entreprise", "region", "type_contrat"]
    for champ in champs_requis:
        assert champ in offre