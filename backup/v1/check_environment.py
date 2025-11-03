#!/usr/bin/env python3
"""
Script de vérification complète de l'environnement.

Vérifie que tout est configuré correctement pour le fonctionnement de l'application.
"""

import sys
import os
from pathlib import Path

# Couleurs
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def check_python_version():
    """Vérifie la version Python."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"{GREEN}✓ Python {version.major}.{version.minor}.{version.micro}{NC}")
        return True
    else:
        print(f"{RED}✗ Python 3.10+ requis (version actuelle: {version.major}.{version.minor}.{version.micro}){NC}")
        return False


def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    required = [
        'flask',
        'flask_sqlalchemy',
        'flask_jwt_extended',
        'marshmallow',
        'pymysql',
        'cryptography',
    ]
    
    missing = []
    for dep in required:
        try:
            __import__(dep)
            print(f"{GREEN}✓ {dep}{NC}")
        except ImportError:
            print(f"{RED}✗ {dep} manquant{NC}")
            missing.append(dep)
    
    return len(missing) == 0


def check_database():
    """Vérifie la connexion à la base de données."""
    try:
        from web.app import create_app
        from web.database import db
        
        app = create_app()
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            print(f"{GREEN}✓ Connexion base de données OK{NC}")
            return True
    except Exception as e:
        print(f"{RED}✗ Erreur connexion base de données: {e}{NC}")
        return False


def check_env_vars():
    """Vérifie les variables d'environnement."""
    required = ['DATABASE_URL']
    optional = ['JWT_SECRET_KEY', 'API_KEYS_ENCRYPTION_KEY']
    
    all_ok = True
    
    for var in required:
        if os.getenv(var):
            print(f"{GREEN}✓ {var} défini{NC}")
        else:
            print(f"{RED}✗ {var} manquant (requis){NC}")
            all_ok = False
    
    for var in optional:
        if os.getenv(var):
            print(f"{GREEN}✓ {var} défini{NC}")
        else:
            print(f"{YELLOW}⚠ {var} non défini (recommandé){NC}")
    
    return all_ok


def check_directories():
    """Vérifie que les répertoires nécessaires existent."""
    required_dirs = [
        'releases',
        'uploads',
        'logs',
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"{GREEN}✓ Répertoire {dir_name}/ existe{NC}")
        else:
            print(f"{YELLOW}⚠ Répertoire {dir_name}/ manquant (sera créé automatiquement){NC}")
            dir_path.mkdir(exist_ok=True)
    
    return True


def check_external_tools():
    """Vérifie la présence d'outils externes."""
    import shutil
    
    tools = {
        'mediainfo': 'MediaInfo (optionnel pour TV)',
        'mkvmerge': 'mkvmerge (optionnel pour TV)',
        'rar': 'RAR CLI (optionnel pour RAR)',
    }
    
    for tool, desc in tools.items():
        if shutil.which(tool):
            print(f"{GREEN}✓ {tool} installé{NC}")
        else:
            print(f"{YELLOW}⚠ {tool} non trouvé ({desc}){NC}")


def check_admin_user():
    """Vérifie qu'un utilisateur admin existe."""
    try:
        from web.app import create_app
        from web.database import db
        from web.models.user import User, UserRole
        
        app = create_app()
        with app.app_context():
            admin = User.query.filter_by(role=UserRole.ADMIN).first()
            if admin:
                print(f"{GREEN}✓ Utilisateur admin trouvé: {admin.username}{NC}")
                return True
            else:
                print(f"{YELLOW}⚠ Aucun utilisateur admin trouvé{NC}")
                print(f"   Exécutez: python web/scripts/seed_admin.py admin password")
                return False
    except Exception as e:
        print(f"{RED}✗ Erreur vérification admin: {e}{NC}")
        return False


def main():
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}VÉRIFICATION ENVIRONNEMENT - Packer de Release{NC}")
    print(f"{BLUE}{'='*80}{NC}\n")
    
    checks = [
        ("Version Python", check_python_version),
        ("Dépendances Python", check_dependencies),
        ("Variables d'environnement", check_env_vars),
        ("Répertoires", check_directories),
        ("Connexion base de données", check_database),
        ("Utilisateur admin", check_admin_user),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{BLUE}📋 {name}{NC}")
        result = check_func()
        results.append((name, result))
    
    print(f"\n{BLUE}🔧 Outils externes (optionnels){NC}")
    check_external_tools()
    
    print(f"\n{BLUE}{'='*80}{NC}")
    print(f"{BLUE}RÉSUMÉ{NC}")
    print(f"{BLUE}{'='*80}{NC}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓ PASS{NC}" if result else f"{RED}✗ FAIL{NC}"
        print(f"{name:30} : {status}")
    
    print(f"\nTotal: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print(f"\n{GREEN}✅ L'environnement est prêt !{NC}")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  Certaines vérifications ont échoué{NC}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
