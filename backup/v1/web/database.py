"""
Configuration base de données SQLAlchemy pour Flask.
"""

import logging

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

# Instance SQLAlchemy (initialisée dans create_app)
db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask) -> None:
    """
    Initialise la base de données avec l'application Flask.

    Args:
        app: Instance Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)

    logger.info("Base de données initialisée")
