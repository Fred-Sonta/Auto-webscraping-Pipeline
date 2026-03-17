from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from api.routes import register_routes
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__)
    
    # Autorise les requêtes provenant d'autres ports 
    CORS(app)

    # Configuration de l'interface Swagger 
    api = Api(
        app,
        version='1.0',
        title='Observatoire de l\'Emploi API',
        description='API REST professionnelle pour l\'accès aux données du marché de l\'emploi ivoirien.',
        doc='/docs', # L'URL magique pour voir l'interface !
        default='Données',
        default_label='Endpoints d\'accès aux données'
    )

    # Initialisation des routes
    register_routes(api)

    return app

if __name__ == '__main__':
    app = create_app()
    # Le mode debug est actif pour le développement
    app.run(host='0.0.0.0', port=5000, debug=True)

