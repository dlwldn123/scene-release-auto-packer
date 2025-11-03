#!/usr/bin/env python3
"""
Script de test complet pour vérifier toutes les fonctionnalités implémentées.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def test_imports():
    """Test 1: Vérifier que tous les imports fonctionnent."""
    print("=" * 80)
    print("TEST 1: Vérification des imports")
    print("=" * 80)

    errors = []

    try:
        from web.app import create_app

        print("✓ web.app.create_app")
    except Exception as e:
        print(f"✗ web.app.create_app: {e}")
        errors.append(str(e))

    try:
        from web.database import db, init_db

        print("✓ web.database")
    except Exception as e:
        print(f"✗ web.database: {e}")
        errors.append(str(e))

    try:
        from web.models import (
            ApiConfig,
            Artifact,
            Destination,
            GlobalPreference,
            Job,
            JobLog,
            NfoTemplate,
            User,
            UserPreference,
        )

        print("✓ web.models (tous les modèles)")
    except Exception as e:
        print(f"✗ web.models: {e}")
        errors.append(str(e))

    try:
        from web.blueprints.auth import auth_bp

        print("✓ web.blueprints.auth")
    except Exception as e:
        print(f"✗ web.blueprints.auth: {e}")
        errors.append(str(e))

    try:
        from web.blueprints.jobs import jobs_bp

        print("✓ web.blueprints.jobs")
    except Exception as e:
        print(f"✗ web.blueprints.jobs: {e}")
        errors.append(str(e))

    try:
        from web.blueprints.wizard import wizard_bp

        print("✓ web.blueprints.wizard")
    except Exception as e:
        print(f"✗ web.blueprints.wizard: {e}")
        errors.append(str(e))

    try:
        from web.blueprints.preferences import preferences_bp

        print("✓ web.blueprints.preferences")
    except Exception as e:
        print(f"✗ web.blueprints.preferences: {e}")
        errors.append(str(e))

    try:
        from web.services.packaging import PackagingService

        print("✓ web.services.packaging")
    except Exception as e:
        print(f"✗ web.services.packaging: {e}")
        errors.append(str(e))

    try:
        from web.schemas.auth import LoginSchema
        from web.schemas.job import JobResponseSchema
        from web.schemas.preference import PreferenceSchema
        from web.schemas.wizard import WizardPackRequestSchema

        print("✓ web.schemas (tous les schémas)")
    except Exception as e:
        print(f"✗ web.schemas: {e}")
        errors.append(str(e))

    try:
        from web.auth import admin_required, operator_or_admin_required

        print("✓ web.auth (décorateurs)")
    except Exception as e:
        print(f"✗ web.auth: {e}")
        errors.append(str(e))

    try:
        from web.crypto import get_cipher

        print("✓ web.crypto")
    except Exception as e:
        print(f"✗ web.crypto: {e}")
        errors.append(str(e))

    try:
        from src.packer_cli import main as cli_main

        print("✓ src.packer_cli")
    except Exception as e:
        print(f"✗ src.packer_cli: {e}")
        errors.append(str(e))

    print(f"\nRésultat: {len(errors)} erreur(s)")
    return len(errors) == 0


def test_app_creation():
    """Test 2: Vérifier que l'application Flask peut être créée."""
    print("\n" + "=" * 80)
    print("TEST 2: Création de l'application Flask")
    print("=" * 80)

    try:
        import os

        # Utiliser SQLite pour les tests (pas besoin de MySQL)
        os.environ["DATABASE_URL"] = "sqlite:///test.db"

        from web.app import create_app

        app = create_app()
        print("✓ Application Flask créée")

        # Vérifier les blueprints enregistrés
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        expected_blueprints = ["auth", "jobs", "wizard", "preferences", "api", "tv"]

        missing = [bp for bp in expected_blueprints if bp not in blueprint_names]
        if missing:
            print(f"✗ Blueprints manquants: {missing}")
            return False

        print(f"✓ Blueprints enregistrés: {blueprint_names}")
        return True

    except Exception as e:
        print(f"✗ Erreur création application: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_models():
    """Test 3: Vérifier que les modèles sont bien définis."""
    print("\n" + "=" * 80)
    print("TEST 3: Vérification des modèles")
    print("=" * 80)

    try:
        from web.models import (
            ApiConfig,
            Artifact,
            Destination,
            GlobalPreference,
            Job,
            JobLog,
            NfoTemplate,
            User,
            UserPreference,
        )
        from web.models.job import JobStatus
        from web.models.user import UserRole

        # Vérifier User
        assert hasattr(User, "username")
        assert hasattr(User, "set_password")
        assert hasattr(User, "check_password")
        assert hasattr(User, "is_admin")
        print("✓ Modèle User")

        # Vérifier Job
        assert hasattr(Job, "job_id")
        assert hasattr(Job, "start")
        assert hasattr(Job, "complete")
        assert hasattr(Job, "fail")
        assert hasattr(Job, "add_log")
        print("✓ Modèle Job")

        # Vérifier UserPreference
        assert hasattr(UserPreference, "get_value")
        assert hasattr(UserPreference, "set_value")
        print("✓ Modèle UserPreference")

        # Vérifier ApiConfig
        assert hasattr(ApiConfig, "get_api_key")
        assert hasattr(ApiConfig, "set_api_key")
        print("✓ Modèle ApiConfig")

        # Vérifier Destination
        assert hasattr(Destination, "get_password")
        assert hasattr(Destination, "set_password")
        print("✓ Modèle Destination")

        # Vérifier enums
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.OPERATOR.value == "operator"
        assert JobStatus.PENDING.value == "pending"
        print("✓ Enums (UserRole, JobStatus)")

        return True

    except Exception as e:
        print(f"✗ Erreur vérification modèles: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_schemas():
    """Test 4: Vérifier que les schémas Marshmallow fonctionnent."""
    print("\n" + "=" * 80)
    print("TEST 4: Vérification des schémas Marshmallow")
    print("=" * 80)

    try:
        from web.schemas.auth import LoginSchema
        from web.schemas.job import JobResponseSchema
        from web.schemas.preference import PreferenceSchema
        from web.schemas.wizard import WizardPackRequestSchema

        # Test LoginSchema
        schema = LoginSchema()
        data = {"username": "test", "password": "test"}
        result = schema.load(data)
        assert result["username"] == "test"
        print("✓ LoginSchema")

        # Test PreferenceSchema
        pref_schema = PreferenceSchema()
        pref_data = {
            "preference_key": "test_key",
            "preference_value": {"test": "value"},
        }
        result = pref_schema.load(pref_data)
        assert result["preference_key"] == "test_key"
        print("✓ PreferenceSchema")

        return True

    except Exception as e:
        print(f"✗ Erreur vérification schémas: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_cli_structure():
    """Test 5: Vérifier que le CLI a la bonne structure."""
    print("\n" + "=" * 80)
    print("TEST 5: Vérification structure CLI")
    print("=" * 80)

    try:
        import argparse

        from src.packer_cli import main

        # Vérifier que le fichier existe et peut être importé
        cli_file = Path(__file__).parent.parent / "src" / "packer_cli.py"
        assert cli_file.exists(), f"packer_cli.py n'existe pas à {cli_file}"
        print(f"✓ Fichier packer_cli.py existe: {cli_file}")

        # Vérifier que main existe
        assert callable(main), "main n'est pas callable"
        print("✓ Fonction main() existe")

        return True

    except Exception as e:
        print(f"✗ Erreur vérification CLI: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_crypto():
    """Test 6: Vérifier que le chiffrement fonctionne."""
    print("\n" + "=" * 80)
    print("TEST 6: Vérification chiffrement")
    print("=" * 80)

    try:
        from web.crypto import get_cipher

        cipher = get_cipher()

        # Test chiffrement/déchiffrement
        test_data = b"test_secret_data"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)

        assert decrypted == test_data, "Chiffrement/déchiffrement échoué"
        print("✓ Chiffrement/déchiffrement fonctionne")

        return True

    except Exception as e:
        print(f"✗ Erreur vérification chiffrement: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests."""
    print("\n" + "=" * 80)
    print("TESTS COMPLETS - Vérification fonctionnalités implémentées")
    print("=" * 80)

    tests = [
        test_imports,
        test_app_creation,
        test_models,
        test_schemas,
        test_cli_structure,
        test_crypto,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} a échoué avec exception: {e}")
            results.append(False)

    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i}. {test.__name__}: {status}")

    print(f"\nTotal: {passed}/{total} tests passés")

    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
