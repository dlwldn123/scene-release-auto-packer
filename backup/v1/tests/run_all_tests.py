"""
Script pour exécuter tous les tests avec rapport détaillé.
"""

#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Exécute tous les tests et génère un rapport."""
    root_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("EXÉCUTION COMPLÈTE DES TESTS")
    print("=" * 80)
    print()

    # Tests unitaires
    print("📦 Tests unitaires...")
    cmd_unit = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_*.py",
        "-v",
        "--tb=short",
        "--cov=web.services",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
    ]

    result_unit = subprocess.run(cmd_unit, cwd=root_dir)

    print()
    print("=" * 80)
    print("TESTS D'INTÉGRATION")
    print("=" * 80)
    print()

    # Tests d'intégration
    cmd_integration = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_integration_*.py",
        "-v",
        "--tb=short",
    ]

    result_integration = subprocess.run(cmd_integration, cwd=root_dir)

    print()
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    total_failed = result_unit.returncode + result_integration.returncode

    if total_failed == 0:
        print("✅ Tous les tests sont passés!")
        return 0
    else:
        print(f"⚠️  {total_failed} suite(s) de tests ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
