#!/usr/bin/env python3
"""
Script de validation complète du projet - Vérifie que tout est en place.

Ce script vérifie :
- Structure des fichiers
- Imports Python
- Configuration Docker
- Tests disponibles
- Documentation
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Couleurs pour output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

errors = []
warnings = []
success = []


def check_file_exists(filepath: str, description: str) -> bool:
    """Vérifie qu'un fichier existe."""
    if Path(filepath).exists():
        success.append(f"✓ {description}: {filepath}")
        return True
    else:
        errors.append(f"✗ {description} manquant: {filepath}")
        return False


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Vérifie qu'un répertoire existe."""
    if Path(dirpath).is_dir():
        success.append(f"✓ {description}: {dirpath}")
        return True
    else:
        warnings.append(f"⚠ {description} manquant: {dirpath}")
        return False


def check_import(module: str, description: str) -> bool:
    """Vérifie qu'un module Python peut être importé."""
    try:
        __import__(module)
        success.append(f"✓ {description}: {module}")
        return True
    except ImportError as e:
        errors.append(f"✗ {description} non importable: {module} - {e}")
        return False
    except Exception as e:
        warnings.append(f"⚠ {description} erreur: {module} - {e}")
        return False


def check_docker_config() -> Tuple[int, int]:
    """Vérifie la configuration Docker."""
    docker_ok = 0
    docker_total = 0
    
    # Dockerfile
    docker_total += 1
    if check_file_exists("Dockerfile", "Dockerfile"):
        docker_ok += 1
    
    # docker-compose.yml
    docker_total += 1
    if check_file_exists("docker-compose.yml", "docker-compose.yml"):
        docker_ok += 1
    
    # start_docker.sh
    docker_total += 1
    if check_file_exists("start_docker.sh", "Script démarrage Docker"):
        docker_ok += 1
        # Vérifier exécutable
        if os.access("start_docker.sh", os.X_OK):
            success.append("✓ start_docker.sh est exécutable")
        else:
            warnings.append("⚠ start_docker.sh n'est pas exécutable")
    
    return docker_ok, docker_total


def check_services() -> Tuple[int, int]:
    """Vérifie les services implémentés."""
    services_ok = 0
    services_total = 0
    
    service_files = [
        ("web/services/packaging.py", "Service Packaging"),
        ("web/services/ftp_upload.py", "Service FTP Upload"),
        ("web/services/template_renderer.py", "Service Template Renderer"),
    ]
    
    for filepath, description in service_files:
        services_total += 1
        if check_file_exists(filepath, description):
            services_ok += 1
    
    # Vérifier APIs TV
    services_total += 1
    if check_file_exists("src/metadata/tv_apis.py", "Service APIs TV"):
        services_ok += 1
    
    # Vérifier packaging DOCS
    services_total += 1
    if check_file_exists("src/packaging/docs_packer.py", "Service Packaging DOCS"):
        services_ok += 1
    
    return services_ok, services_total


def check_blueprints() -> Tuple[int, int]:
    """Vérifie les blueprints Flask."""
    blueprints_ok = 0
    blueprints_total = 0
    
    blueprint_files = [
        ("web/blueprints/auth.py", "Blueprint Auth"),
        ("web/blueprints/jobs.py", "Blueprint Jobs"),
        ("web/blueprints/wizard.py", "Blueprint Wizard"),
        ("web/blueprints/preferences.py", "Blueprint Preferences"),
        ("web/blueprints/export.py", "Blueprint Export"),
        ("web/blueprints/api_config.py", "Blueprint API Config"),
        ("web/blueprints/health.py", "Blueprint Health"),
    ]
    
    for filepath, description in blueprint_files:
        blueprints_total += 1
        if check_file_exists(filepath, description):
            blueprints_ok += 1
    
    return blueprints_ok, blueprints_total


def check_tests() -> Tuple[int, int]:
    """Vérifie les tests."""
    tests_ok = 0
    tests_total = 0
    
    # Structure tests E2E
    tests_total += 1
    if check_directory_exists("tests/e2e", "Dossier tests E2E"):
        tests_ok += 1
        # Compter fichiers de tests
        test_files = list(Path("tests/e2e").glob("test_*.py"))
        if test_files:
            success.append(f"✓ {len(test_files)} fichiers de tests E2E trouvés")
        else:
            warnings.append("⚠ Aucun fichier test_*.py dans tests/e2e")
    
    # Tests unitaires
    test_unit_files = [
        "tests/test_ftp_upload.py",
        "tests/test_docs_packaging.py",
        "tests/test_tv_apis.py",
    ]
    
    for filepath in test_unit_files:
        tests_total += 1
        if check_file_exists(filepath, f"Test unitaire {Path(filepath).stem}"):
            tests_ok += 1
    
    return tests_ok, tests_total


def check_documentation() -> Tuple[int, int]:
    """Vérifie la documentation."""
    docs_ok = 0
    docs_total = 0
    
    doc_files = [
        ("DEPLOYMENT.md", "Documentation déploiement"),
        ("ITERATION_LOG.md", "Journal itérations"),
        ("RMD.md", "Release Management Document"),
        ("DOCKER_SUMMARY.md", "Résumé Docker"),
        ("tests/e2e/README.md", "Documentation tests E2E"),
    ]
    
    for filepath, description in doc_files:
        docs_total += 1
        if check_file_exists(filepath, description):
            docs_ok += 1
    
    return docs_ok, docs_total


def main():
    """Fonction principale."""
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}VALIDATION COMPLÈTE DU PROJET - Packer de Release{NC}")
    print(f"{BLUE}{'='*80}{NC}\n")
    
    # Vérifier structure de base
    print(f"{BLUE}📁 Structure de base{NC}")
    check_directory_exists("web", "Dossier web")
    check_directory_exists("src", "Dossier src")
    check_directory_exists("tests", "Dossier tests")
    check_file_exists("requirements.txt", "requirements.txt")
    check_file_exists("web/app.py", "Application Flask")
    print()
    
    # Vérifier Docker
    print(f"{BLUE}🐳 Configuration Docker{NC}")
    docker_ok, docker_total = check_docker_config()
    print()
    
    # Vérifier Services
    print(f"{BLUE}⚙️  Services implémentés{NC}")
    services_ok, services_total = check_services()
    print()
    
    # Vérifier Blueprints
    print(f"{BLUE}🔵 Blueprints Flask{NC}")
    blueprints_ok, blueprints_total = check_blueprints()
    print()
    
    # Vérifier Tests
    print(f"{BLUE}🧪 Tests{NC}")
    tests_ok, tests_total = check_tests()
    print()
    
    # Vérifier Documentation
    print(f"{BLUE}📚 Documentation{NC}")
    docs_ok, docs_total = check_documentation()
    print()
    
    # Résumé
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}RÉSUMÉ{NC}")
    print(f"{BLUE}{'='*80}{NC}\n")
    
    categories = [
        ("Docker", docker_ok, docker_total),
        ("Services", services_ok, services_total),
        ("Blueprints", blueprints_ok, blueprints_total),
        ("Tests", tests_ok, tests_total),
        ("Documentation", docs_ok, docs_total),
    ]
    
    total_ok = sum(ok for _, ok, _ in categories)
    total_items = sum(total for _, _, total in categories)
    
    for name, ok, total in categories:
        percentage = (ok / total * 100) if total > 0 else 0
        status_color = GREEN if ok == total else YELLOW if ok > 0 else RED
        print(f"{name:15} : {status_color}{ok}/{total}{NC} ({percentage:.0f}%)")
    
    print(f"\n{'Total':15} : {GREEN if total_ok == total_items else YELLOW}{total_ok}/{total_items}{NC}")
    
    # Afficher erreurs et warnings
    if errors:
        print(f"\n{RED}ERREURS:{NC}")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\n{YELLOW}AVERTISSEMENTS:{NC}")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print(f"\n{GREEN}✅ Tous les fichiers essentiels sont présents !{NC}")
    
    # Code de retour
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
