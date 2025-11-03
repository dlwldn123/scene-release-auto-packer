"""
Script pour exécuter tous les tests E2E et générer un rapport.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests():
    """Exécute tous les tests E2E et génère un rapport."""
    root_dir = Path(__file__).parent.parent

    print("=" * 80)
    print("EXÉCUTION TESTS E2E - Validation Fonctionnalités Existantes")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Exécuter pytest avec rapport détaillé
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/e2e/",
        "-v",
        "--tb=short",
        "--cov=web",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    result = subprocess.run(cmd, cwd=root_dir)

    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✓ TOUS LES TESTS E2E SONT PASSÉS")
    else:
        print(f"✗ {result.returncode} test(s) ont échoué")
    print("=" * 80)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
