from flask import Flask, Response
from flask_restx import Api
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from api.routes import register_routes
from db.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

# 1. On initialise l'API Swagger normalement
api = Api(
    app,
    version='1.0',
    title='Observatoire de l\'Emploi API',
    description='API REST professionnelle pour l\'accès aux données WWR.',
    doc='/docs'
)
Base.metadata.create_all(bind=engine)
register_routes(api)

# 2. On lance la collecte Prometheus, mais on lui interdit de créer sa route (path=None)
metrics = PrometheusMetrics(app, path=None)
metrics.info('app_info', 'API Observatoire Emploi', version='1.0')

# 3. On ajoute une route dédiée pour les métriques Prometheus
@app.route('/metrics')
def metrics_endpoint():
    # generate_latest() récupère toutes les données collectées en arrière-plan
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)