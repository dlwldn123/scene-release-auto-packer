#!/usr/bin/env python3
"""
Script utilitaire pour gérer les configurations API.

Permet de configurer facilement les APIs externes.
"""

import argparse
import json
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from web.app import create_app
from web.database import db
from web.models.api_config import ApiConfig
from web.models.user import User, UserRole


def list_apis():
    """Liste toutes les configurations API."""
    app = create_app()

    with app.app_context():
        configs = ApiConfig.query.all()

        if not configs:
            print("Aucune configuration API trouvée.")
            return

        print("\n📋 Configurations API disponibles:\n")
        for config in configs:
            status = "✅ Activé" if config.enabled else "❌ Désactivé"
            print(f"  {config.api_name.upper()}: {status}")
            print(f"    User ID: {config.user_id}")
            print(f"    Créé: {config.created_at}")
            print()


def add_api(api_name, api_key, user_key=None, enabled=True):
    """Ajoute ou met à jour une configuration API."""
    app = create_app()

    with app.app_context():
        # Récupérer premier admin pour attribution
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            print("❌ Aucun utilisateur admin trouvé. Créez d'abord un admin.")
            return False

        # Vérifier si config existe
        config = ApiConfig.query.filter_by(api_name=api_name, user_id=admin.id).first()

        api_data = {"api_key": api_key}
        if user_key:
            api_data["user_key"] = user_key

        if config:
            config.set_api_key(api_data)
            config.enabled = enabled
            print(f"✓ Configuration API '{api_name}' mise à jour")
        else:
            config = ApiConfig(
                api_name=api_name,
                user_id=admin.id,
                enabled=enabled,
            )
            config.set_api_key(api_data)
            db.session.add(config)
            print(f"✓ Configuration API '{api_name}' créée")

        db.session.commit()
        return True


def test_api(api_name):
    """Teste une configuration API."""
    app = create_app()

    with app.app_context():
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            print("❌ Aucun utilisateur admin trouvé.")
            return False

        config = ApiConfig.query.filter_by(api_name=api_name, user_id=admin.id).first()

        if not config:
            print(f"❌ Configuration API '{api_name}' introuvable.")
            return False

        if not config.enabled:
            print(f"⚠️  Configuration API '{api_name}' désactivée.")
            return False

        print(f"🧪 Test de l'API {api_name.upper()}...")

        try:
            if api_name == "omdb":
                import requests

                api_data = config.get_api_key()
                api_key = api_data.get("api_key")
                if not api_key:
                    print("❌ Clé API manquante")
                    return False

                # Test simple
                response = requests.get(
                    "http://www.omdbapi.com/",
                    params={"apikey": api_key, "t": "Breaking Bad", "type": "series"},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Response") == "True":
                        print(f"✅ API OMDb fonctionnelle: {data.get('Title')}")
                        return True
                    else:
                        print(f"❌ Erreur API: {data.get('Error')}")
                        return False
                else:
                    print(f"❌ Erreur HTTP: {response.status_code}")
                    return False

            elif api_name == "tvdb":
                from src.metadata.tvdb_auth import TvdbAuthenticator

                api_data = config.get_api_key()
                api_key = api_data.get("api_key")
                user_key = api_data.get("user_key")

                if not api_key or not user_key:
                    print("❌ Clés API manquantes (api_key et user_key requis)")
                    return False

                auth = TvdbAuthenticator(api_key, user_key)
                token = auth.get_token()
                if token:
                    print("✅ API TVDB authentifiée avec succès")
                    return True
                else:
                    print("❌ Échec authentification TVDB")
                    return False

            elif api_name == "tmdb":
                import requests

                api_data = config.get_api_key()
                api_key = api_data.get("api_key")
                if not api_key:
                    print("❌ Clé API manquante")
                    return False

                response = requests.get(
                    "https://api.themoviedb.org/3/search/tv",
                    params={"api_key": api_key, "query": "Breaking Bad"},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        print(f"✅ API TMDb fonctionnelle")
                        return True
                    else:
                        print("❌ Aucun résultat trouvé")
                        return False
                else:
                    print(f"❌ Erreur HTTP: {response.status_code}")
                    return False

            else:
                print(f"⚠️  Test non implémenté pour '{api_name}'")
                return False

        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Gestion des configurations API")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Liste
    subparsers.add_parser("list", help="Liste toutes les configurations API")

    # Ajouter
    add_parser = subparsers.add_parser(
        "add", help="Ajoute ou met à jour une configuration API"
    )
    add_parser.add_argument(
        "api_name",
        choices=["omdb", "tvdb", "tmdb", "openlibrary", "googlebooks"],
        help="Nom de l'API",
    )
    add_parser.add_argument("api_key", help="Clé API")
    add_parser.add_argument("--user-key", help="Clé utilisateur (pour TVDB)")
    add_parser.add_argument("--disabled", action="store_true", help="Désactiver l'API")

    # Test
    test_parser = subparsers.add_parser("test", help="Teste une configuration API")
    test_parser.add_argument(
        "api_name", choices=["omdb", "tvdb", "tmdb"], help="Nom de l'API à tester"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        list_apis()
    elif args.command == "add":
        add_api(args.api_name, args.api_key, args.user_key, enabled=not args.disabled)
    elif args.command == "test":
        test_api(args.api_name)


if __name__ == "__main__":
    main()
