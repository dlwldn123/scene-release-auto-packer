# 📦 Packer de Release - Scene Ebook/TV/DOCS Packer

Application complète de packaging de releases Scene (EBOOK, TV, DOCS) avec interface web et CLI.

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Démarrer tous les services
./start_docker.sh

# Accéder à l'application
# Interface Web: http://localhost:5000
# Health Check: http://localhost:5000/health
```

### Installation Locale

Voir **[QUICKSTART.md](QUICKSTART.md)** pour guide détaillé.

## 📋 Fonctionnalités

### ✅ Packaging
- **EBOOK** : Packaging conforme Scene Rules 2022
- **TV** : Packaging vidéo avec MediaInfo
- **DOCS** : Packaging documents (PDF, DOCX, TXT)

### ✅ Services
- Upload FTP/SFTP automatique avec retry
- Enrichissement métadonnées (OpenLibrary, Google Books, OMDb, TVDB, TMDb)
- Génération NFO/DIZ/SFV
- Multi-volumes ZIP/RAR
- Templates NFO avec placeholders et conditionnelles

### ✅ Interface Web
- Dashboard avec statistiques
- Wizard 12 étapes pour création release
- Gestion utilisateurs/rôles
- Configuration préférences et chemins
- Gestion destinations FTP/SFTP
- Gestion templates NFO

### ✅ CLI
- Packager fichiers individuels
- Batch processing depuis JSON
- Gestion jobs et logs
- Préférences utilisateur

## 🧪 Tests

```bash
# Tests unitaires et intégration
python tests/run_all_tests.py

# Tests E2E (nécessite serveur Flask démarré)
pytest tests/e2e/

# Validation projet
python validate_project.py
```

**Total** : ~91 tests (41 E2E + 23 unitaires + 18 intégration + 11 templates)

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** : Guide démarrage rapide ⭐
- **[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)** : Guide scripts utilitaires
- **[DEPLOYMENT.md](DEPLOYMENT.md)** : Guide déploiement complet
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** : Checklist production
- **[COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)** : Résumé complet final ⭐⭐
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** : Vue d'ensemble du projet
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** : Récapitulatif final complet
- **[ITERATION_LOG.md](ITERATION_LOG.md)** : Journal de progression
- **[RMD.md](RMD.md)** : Release Management Document
- **[tests/e2e/README.md](tests/e2e/README.md)** : Documentation tests E2E

## 🛠️ Validation

```bash
# Valider la structure du projet
python validate_project.py
```

## 📊 Architecture

```
Frontend (React) → Backend Flask → MySQL Database
                      ↓
              Services (Packaging, FTP, APIs, Templates)
```

Voir [FINAL_SUMMARY.md](FINAL_SUMMARY.md) pour détails complets.

## 🔐 Sécurité

- Chiffrement API keys (Fernet)
- Chiffrement mots de passe FTP/SFTP
- Authentification JWT avec refresh
- Rôles admin/operator
- Masquage clés API dans réponses

## 📝 License

[À définir]

## 🤝 Contribution

[À définir]

## 📞 Support

Pour toute question :
1. Consulter **[QUICKSTART.md](QUICKSTART.md)** pour démarrage rapide
2. Consulter **[DEPLOYMENT.md](DEPLOYMENT.md)** pour déploiement
3. Vérifier les logs : `docker-compose logs -f backend`
4. Vérifier health check : `curl http://localhost:5000/health`