"""
Script d'initialisation de la base de données.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from web.app import create_app
from web.database import db


def init_database() -> None:
    """
    Initialise la base de données (création des tables).
    """
    app = create_app()

    with app.app_context():
        print("Création des tables de base de données...")
        db.create_all()
        print("✓ Tables créées avec succès")

        # Créer compte admin initial
        from web.scripts.seed_admin import seed_admin_user

        seed_admin_user()


if __name__ == "__main__":
    init_database()
