"""Flask application factory."""

from __future__ import annotations

from flask import Flask
from flask_jwt_extended import JWTManager

from web.config import get_config
from web.extensions import db, migrate
from web.security import init_jwt


def create_app(config_name: str | None = None) -> Flask:
    """Create Flask application instance.

    Args:
        config_name: Configuration name ('development', 'production', 'testing').

    Returns:
        Flask application instance.
    """
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize JWT
    jwt = JWTManager(app)
    init_jwt(jwt)

    # Import models to register them with SQLAlchemy
    from web.models import (  # noqa: F401
        Group,
        Job,
        Permission,
        Release,
        Role,
        TokenBlocklist,
        User,
    )

    # Register blueprints
    from web.blueprints.auth import auth_bp
    from web.blueprints.dashboard import dashboard_bp
    from web.blueprints.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    return app
