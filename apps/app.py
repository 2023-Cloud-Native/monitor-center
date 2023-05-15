from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from apps.config import config

db = SQLAlchemy()


def create_app(config_key="local"):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config[config_key])

    # Create database
    db.init_app(app)
    Migrate(app, db)

    # Create blueprint from api template
    from apps.api import views as api_view
    app.register_blueprint(api_view.api)

    return app
