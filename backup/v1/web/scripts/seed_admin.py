"""
Script de seed pour créer le compte admin initial.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from web.app import create_app
from web.database import db
from web.models.user import User, UserRole


def seed_admin_user(
    username: str = "admin", password: str = "admin", email: str = "admin@example.com"
) -> None:
    """
    Crée le compte admin initial si il n'existe pas.

    Args:
        username: Nom d'utilisateur admin (défaut: 'admin')
        password: Mot de passe admin (défaut: 'admin')
        email: Email admin (défaut: 'admin@example.com')
    """
    app = create_app()

    with app.app_context():
        # Vérifier si admin existe déjà
        admin = User.query.filter_by(username=username).first()
        if admin:
            print(f"✓ Compte admin '{username}' existe déjà")
            return

        # Créer admin
        admin = User(
            username=username,
            email=email,
            role=UserRole.ADMIN,
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print(f"✓ Compte admin '{username}' créé avec succès")
        print(f"  ⚠️  ATTENTION: Changez le mot de passe par défaut en production!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Créer le compte admin initial")
    parser.add_argument("--username", default="admin", help="Nom d'utilisateur admin")
    parser.add_argument("--password", default="admin", help="Mot de passe admin")
    parser.add_argument("--email", default="admin@example.com", help="Email admin")

    args = parser.parse_args()

    seed_admin_user(username=args.username, password=args.password, email=args.email)
