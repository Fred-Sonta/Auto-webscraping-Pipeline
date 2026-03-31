from flask_restx import fields

def get_models(api):
    entreprise_model = api.model('Entreprise', {
        'id': fields.Integer,
        'nom': fields.String
    })

    offre_model = api.model('Offre', {
        'id': fields.Integer,
        'id_externe': fields.String,
        'url': fields.String,
        'titre_poste': fields.String,
        'entreprise': fields.Nested(entreprise_model),
        'region': fields.String,
        'type_contrat': fields.String,
        'salaire': fields.String,
        'tags': fields.String,
        'logo_url': fields.String,
        'date_publication': fields.String
    })

    paginated_offres = api.model('PaginatedOffres', {
        'page': fields.Integer,
        'limit': fields.Integer,
        'total_items': fields.Integer,
        'data': fields.List(fields.Nested(offre_model))
    })

    return entreprise_model, offre_model, paginated_offres

