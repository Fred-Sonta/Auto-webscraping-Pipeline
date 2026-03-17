from flask_restx import fields

def get_models(api):
    """Définit et retourne les modèles de données pour la documentation Swagger."""
    
    entreprise_model = api.model('Entreprise', {
        'id': fields.Integer(description="ID unique de l'entreprise dans la base"),
        'nom': fields.String(description="Nom de l'entreprise")
    })

    offre_model = api.model('Offre', {
        'id': fields.Integer(description="ID unique de l'offre en base"),
        'id_emploi_ci': fields.String(description="Identifiant d'origine sur Emploi.ci"),
        'url': fields.String(description="Lien direct vers l'annonce"),
        'titre_poste': fields.String(description="Intitulé du poste"),
        'entreprise': fields.Nested(entreprise_model, description="L'entreprise qui recrute"),
        'ville': fields.String(description="Lieu de travail"),
        'type_contrat': fields.String(description="CDI, CDD, Stage..."),
        'niveau_etude_requis': fields.String(description="Bac, Licence, Master..."),
        'experience_requise': fields.String(description="Années d'expérience"),
        'date_publication': fields.String(description="Date de l'annonce")
    })

    # Modèle spécifique pour la pagination exigée au niveau Argent
    paginated_offres = api.model('PaginatedOffres', {
        'page': fields.Integer(description="Page actuelle"),
        'limit': fields.Integer(description="Nombre d'éléments par page"),
        'total_items': fields.Integer(description="Nombre total d'offres correspondantes"),
        'data': fields.List(fields.Nested(offre_model), description="Liste des offres")
    })

    return entreprise_model, offre_model, paginated_offres
