from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from api.database import DBSession
from apps.config import config


def create_app(config_key="local"):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config[config_key])
    metrics = PrometheusMetrics(app)
    metrics.info("app_info", "Application Info", verion=1.0)

    # Create blueprint from api template
    from apps.api import views as api_view

    app.register_blueprint(api_view.api)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        DBSession.remove()

    return app
