"""
Script de test complet avec SQLite pour éviter MySQL.
"""

import os
import sys
from pathlib import Path

# Forcer SQLite pour les tests
os.environ["DATABASE_URL"] = "sqlite:///test_packer.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["API_KEYS_ENCRYPTION_KEY"] = "test-encryption-key-32-bytes-long!!"

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from web.app import create_app
from web.database import db
from web.scripts.seed_admin import seed_admin_user


def setup_test_db():
    """Configure la base de données de test."""
    app = create_app()
    with app.app_context():
        # Supprimer tables existantes
        db.drop_all()
        # Créer tables
        db.create_all()
        print("✓ Base de données de test créée")

        # Créer compte admin de test
        seed_admin_user(username="admin", password="admin", email="admin@test.com")
        print("✓ Compte admin de test créé")


if __name__ == "__main__":
    print("Configuration de la base de données de test...")
    setup_test_db()
    print("\n✓ Prêt pour les tests!")
