#!/usr/bin/env python3
"""
Application Flask principale pour interface web Scene Ebook Packer.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_caching import Cache
from flask_compress import Compress
from flask_cors import CORS

# Imports modules locaux
from src.exceptions import ApplicationError
from src.metadata import (
    MetadataEnricher,
    detect_format,
    extract_epub_metadata,
    extract_mobi_metadata,
    extract_pdf_metadata,
)
from src.packer import process_ebook
from src.scene_rules import (
    get_cached_rule,
    grab_all_rules,
    grab_and_cache_rule,
    grab_rules_list,
    list_cached_rules,
)
from src.utils import generate_release_name, validate_release
from src.video import pack_tv_release

# Database
from web.database import db, init_db

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """
    Charge configuration depuis config.yaml ou ENV vars.

    Returns:
        Dictionnaire de configuration

    Raises:
        ConfigurationError: Si erreur lors du chargement
    """
    from src.exceptions import ConfigurationError

    config_path = Path("config/config.yaml")

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        # Override avec variables d'environnement (priorité)
        web_config = config.get("web", {})
        # Valeurs par défaut si app non encore créée
        os.environ.setdefault("FLASK_DEBUG", str(web_config.get("debug", True)))
        os.environ.setdefault("FLASK_RUN_HOST", web_config.get("host", "0.0.0.0"))
        os.environ.setdefault("FLASK_RUN_PORT", str(web_config.get("port", 5000)))

        return config
    except Exception as e:
        logger.error(f"Erreur chargement configuration: {e}", exc_info=True)
        raise ConfigurationError(f"Impossible de charger la configuration: {e}") from e


CONFIG = load_config()


def create_app() -> Flask:
    """
    Application factory (meilleures pratiques Flask).

    Valide l'environnement au démarrage et configure l'application Flask.

    Returns:
        Instance Flask configurée

    Raises:
        EnvironmentValidationError: Si validation environnement échoue
    """
    # Valider environnement avant création app
    from web.config import get_config_from_env
    from web.utils.env_validation import validate_environment

    try:
        validate_environment()
    except Exception as e:
        # En développement, on peut continuer avec warnings
        is_production = (
            os.getenv("FLASK_ENV") == "production"
            or os.getenv("ENVIRONMENT") == "production"
        )
        if is_production:
            logger.error(f"❌ Erreur validation environnement: {e}")
            raise  # En production, fail fast
        else:
            logger.warning(
                f"⚠️  Validation environnement échouée (mode dev, continuation): {e}"
            )

    app = Flask(__name__)
    CORS(app)
    app.config.from_object(get_config_from_env())
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
    cache = Cache(app)
    Compress(app)

    # Initialize database
    init_db(app)

    # Dossiers configurés
    web_config = CONFIG.get("web", {})
    app.config["RELEASES_FOLDER"] = Path(web_config.get("releases_folder", "releases"))
    app.config["UPLOAD_FOLDER"] = Path(web_config.get("upload_folder", "uploads"))
    app.config["EBOOKS_FOLDER"] = Path(web_config.get("ebooks_folder", "ebooks"))
    app.config["RULES_CACHE_FOLDER"] = Path(
        web_config.get("rules_cache_folder", "rules_cache")
    )
    app.config["NFO_TEMPLATES_FOLDER"] = Path(
        web_config.get("nfo_templates_folder", "templates/nfo")
    )
    app.config["PREFS_FILE"] = Path(web_config.get("prefs_file", "config/prefs.json"))

    # Créer dossiers nécessaires
    app.config["RELEASES_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["EBOOKS_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["RULES_CACHE_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["NFO_TEMPLATES_FOLDER"].mkdir(parents=True, exist_ok=True)

    # Initialize JWT
    from flask_jwt_extended import JWTManager

    jwt = JWTManager(app)

    # Routes principales (vue)
    @app.route("/login")
    def login():
        """Page de connexion."""
        return render_template("login.html")

    @app.route("/")
    def index():
        """Page principale (dashboard) - nécessite authentification côté frontend."""
        return render_template("index.html")

    @app.route("/users")
    def users():
        """Page de gestion des utilisateurs (admin uniquement - vérifié côté frontend)."""
        return render_template("users.html")

    @app.route("/logout")
    def logout():
        """Logout (redirection vers login)."""
        return redirect(url_for("login"))

    # Enregistrer blueprints API (versionnées)
    from web.blueprints.api import api_bp
    from web.blueprints.api_config import api_config_bp
    from web.blueprints.auth import auth_bp
    from web.blueprints.destinations import destinations_bp
    from web.blueprints.export import export_bp
    from web.blueprints.health import health_bp
    from web.blueprints.jobs import jobs_bp
    from web.blueprints.paths import paths_bp
    from web.blueprints.preferences import preferences_bp
    from web.blueprints.templates import templates_bp
    from web.blueprints.tv import tv_bp
    from web.blueprints.users import users_bp
    from web.blueprints.wizard import wizard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(wizard_bp, url_prefix="/api/wizard")
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")
    app.register_blueprint(export_bp, url_prefix="/api/export")
    app.register_blueprint(api_config_bp, url_prefix="/api/config")
    app.register_blueprint(health_bp)  # Pas de préfixe pour /health
    app.register_blueprint(templates_bp, url_prefix="/api/templates")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(paths_bp, url_prefix="/api/paths")
    app.register_blueprint(destinations_bp, url_prefix="/api/destinations")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(tv_bp, url_prefix="/api/tv")

    # Error handlers JSON
    @app.errorhandler(400)
    def handle_400(e):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Requête invalide",
                    "error_type": "ValidationError",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def handle_404(e):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Ressource introuvable",
                    "error_type": "NotFound",
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_500(e):
        logger.error(f"Erreur serveur: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur interne",
                    "error_type": "ServerError",
                }
            ),
            500,
        )

    # Gestion des exceptions personnalisées
    @app.errorhandler(ApplicationError)
    def handle_application_error(e):
        """Gère les exceptions personnalisées de l'application."""
        logger.error(f"Erreur application: {e.message}", exc_info=True)
        return jsonify(e.to_dict()), e.status_code

    # Gestion des erreurs de validation Marshmallow
    from marshmallow import ValidationError as MarshmallowValidationError

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(e):
        """Gère les erreurs de validation Marshmallow."""
        logger.warning(f"Erreur validation: {e.messages}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "True") in ("1", "true", "True")
    logger.info(f"Démarrage serveur Flask: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
