"""Nexus application factory.

The project follows the MVC structure required by the course:
  app/models/       -> Model layer (SQLAlchemy entities and domain rules)
  app/controllers/  -> Controller layer (Flask blueprints, access checks)
  app/views/        -> View layer (Jinja templates + static assets)
"""
from flask import Flask, redirect, url_for

from config import Config
from .extensions import db


def create_app(config_object=Config):
    app = Flask(__name__, template_folder="views/templates")
    app.config.from_object(config_object)

    db.init_app(app)

    from . import models  # noqa: F401  (register tables with SQLAlchemy)

    from .controllers.auth import auth_bp
    from .controllers.profile import profile_bp
    from .controllers.tracking import tracking_bp
    from .controllers.goals import goals_bp
    from .controllers.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.summary"))

    return app
