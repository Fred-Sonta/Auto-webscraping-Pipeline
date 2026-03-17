from flask import request
from flask_restx import Namespace, Resource, abort
from sqlalchemy import or_
from db.database import SessionLocal
from db.models import Offre, Entreprise
from api.schemas import get_models

# Création du "Namespace" (un groupe de routes) pour Swagger
api_namespace = Namespace('data', description='Opérations sur le marché de l\'emploi')

# --- Configuration des paramètres d'URL pour la recherche ---
pagination_parser = api_namespace.parser()
pagination_parser.add_argument('page', type=int, required=False, default=1, help='Numéro de la page')
pagination_parser.add_argument('limit', type=int, required=False, default=10, help='Nombre d\'éléments par page')
pagination_parser.add_argument('query', type=str, required=False, help='Recherche par mot clé (Titre ou Description)')
pagination_parser.add_argument('ville', type=str, required=False, help='Filtrer par ville')
pagination_parser.add_argument('contrat', type=str, required=False, help='Filtrer par type de contrat')

def register_routes(api):
    """Attache les modèles et les routes au namespace."""
    _, offre_model, paginated_offres = get_models(api_namespace)

    @api_namespace.route('/offres')
    class OffreList(Resource):
        @api_namespace.expect(pagination_parser)
        @api_namespace.marshal_with(paginated_offres)
        def get(self):
            """
            Récupérer la liste des offres d'emploi.
            Supporte la pagination et les filtres de recherche (Critère Argent).
            """
            args = pagination_parser.parse_args()
            page = args.get('page', 1)
            limit = args.get('limit', 10)
            search_query = args.get('query')
            ville_filter = args.get('ville')
            contrat_filter = args.get('contrat')

            db = SessionLocal()
            try:
                query = db.query(Offre)

                # Application des filtres dynamiques
                if search_query:
                    query = query.filter(
                        or_(
                            Offre.titre_poste.ilike(f'%{search_query}%'),
                            Offre.description_brute.ilike(f'%{search_query}%')
                        )
                    )
                if ville_filter:
                    query = query.filter(Offre.ville.ilike(f'%{ville_filter}%'))
                if contrat_filter:
                    query = query.filter(Offre.type_contrat.ilike(f'%{contrat_filter}%'))

                # Calcul de la pagination
                total = query.count()
                offset = (page - 1) * limit
                offres = query.offset(offset).limit(limit).all()

                return {
                    'page': page,
                    'limit': limit,
                    'total_items': total,
                    'data': offres
                }
            except Exception as e:
                abort(500, f"Erreur interne du serveur : {str(e)}")
            finally:
                db.close()

    @api_namespace.route('/offres/<int:id>')
    @api_namespace.response(404, 'Offre non trouvée')
    class OffreDetail(Resource):
        @api_namespace.marshal_with(offre_model)
        def get(self, id):
            """Récupérer les détails d'une offre spécifique par son ID interne."""
            db = SessionLocal()
            try:
                offre = db.query(Offre).filter(Offre.id == id).first()
                if not offre:
                    abort(404, "L'offre demandée n'existe pas.")
                return offre
            finally:
                db.close()

    @api_namespace.route('/scrape/async')
    class ScrapeTrigger(Resource):
        def post(self):
            """
            Déclencher une nouvelle collecte de données en arrière-plan.
            (Sera connecté à Celery dans la phase suivante)
            """
            # Placeholder : Ce code sera remplacé par l'appel à Celery
            return {
                "status": "accepté",
                "message": "La tâche de scraping a été placée en file d'attente (Simulation).",
                "task_id": "temp-id-1234"
            }, 202

    # Attacher le namespace à l'API principale
    api.add_namespace(api_namespace, path='/api/v1')
    