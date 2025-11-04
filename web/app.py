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
    cache.init_app(app)

    # Initialize JWT
    jwt = JWTManager(app)
    init_jwt(jwt)

    # Import models to register them with SQLAlchemy
    from web.models import (  # noqa: F401
        Configuration,
        Group,
        Job,
        Permission,
        Release,
        Role,
        Rule,
        TokenBlocklist,
        User,
    )

    # Register blueprints
    from web.blueprints.auth import auth_bp
    from web.blueprints.config import config_bp
    from web.blueprints.dashboard import dashboard_bp
    from web.blueprints.health import health_bp
    from web.blueprints.jobs import jobs_bp
    from web.blueprints.releases import releases_bp
    from web.blueprints.releases_actions import releases_actions_bp
    from web.blueprints.roles import roles_bp
    from web.blueprints.rules import rules_bp
    from web.blueprints.users import users_bp
    from web.blueprints.wizard import wizard_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(wizard_bp, url_prefix="/api")
    app.register_blueprint(releases_bp, url_prefix="/api")
    app.register_blueprint(releases_actions_bp, url_prefix="/api")
    app.register_blueprint(rules_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(roles_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api")
    app.register_blueprint(jobs_bp, url_prefix="/api")

    return app
