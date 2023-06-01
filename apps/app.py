from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from api.models import DBSession
from apps.config import config

db = DBSession()


def create_app(config_key="local"):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config[config_key])
    metrics = PrometheusMetrics(app)
    metrics.info("app_info", "Application Info", verion=1.0)

    # Create blueprint from api template
    from apps.api import views as api_view

    app.register_blueprint(api_view.api)

    return app
