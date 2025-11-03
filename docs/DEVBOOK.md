# 📖 DEVBOOK - eBook Scene Packer v2

**Date de création** : 2025-11-01  
**Version** : 2.0.0  
**Statut** : En développement

---

## 🎯 Vue d'Ensemble

Ce DEVBOOK centralise le suivi de toutes les phases et étapes du projet v2, avec méthodologie TDD, priorités MoSCoW, OKRs et résumés de progression.

**Référence** : Voir `docs/cdc.md` pour le cahier des charges complet.

---

## 🏗️ Décisions Architecturales

**Date de validation** : 2025-11-01  
**Source** : `docs/PROJECT_ANALYSIS_QUESTIONS.md` - Analyse complète projet

### Frontend

#### Structure et Outils
- ✅ **Build Tool** : **Vite** (au lieu de Create React App)
  - Performance optimale (HMR instantané)
  - Support TypeScript natif
  - Configuration : `docs/VITE_SETUP.md`
- ✅ **Framework** : **React 18+** avec **TypeScript strict** dès le début
- ✅ **Routing** : React Router v6 avec structure complète (`/`, `/login`, `/dashboard`, `/releases`, `/rules`, `/users`, `/roles`, `/config`)

#### Design System UI/UX
- ✅ **Design System Complet** : `docs/DESIGN_SYSTEM_UI_UX.md` ⭐
  - Système de couleurs (jour/nuit avec variables CSS)
  - Typographie (polices système, hiérarchie complète)
  - Composants UI (boutons, inputs, cards, tabs, etc.)
  - Bordures élégantes et espacements cohérents
  - Bibliothèque icônes : **Bootstrap Icons** (2 000+ icônes)
  - Thème jour/nuit avec transition fluide
  - Accessibilité WCAG 2.2 AA (contraste, focus, ARIA)
- ✅ **Règles Cursor Complètes** : `.cursor/rules/ui-ux-modern-2025.mdc` ⭐ **NOUVEAU**
  - Règles complètes/intégrales/totales pour Design UX/UI Moderne 2025
  - Meilleures pratiques 2025 (React 19, WCAG 2.2 AA, performance, tendances)
  - Vérifié avec Context7 MCP et recherches web
  - React 19 Features (View Transitions, Activity, useOptimistic)
  - Performance Web Vitals (FCP, LCP, CLS)
  - Accessibilité complète (ARIA, navigation clavier, contraste)
  - Design responsive mobile-first 2025
- ✅ **UI Library** : **Bootstrap 5** (grid, utilities, base components)
- ✅ **Principe** : Design intégralement clair, moderne et cohérent dès le début
- ✅ **Objectifs UX** : Clarté totale, modernité, cohérence, accessibilité
- ✅ **State Management** : Context API pour début (Redux si besoin performance)
- ✅ **Styling** : Bootstrap 5
- ✅ **Structure modulaire** : Composants, Contexts, Services, Hooks, Utils, Pages

#### Authentification Frontend
- ✅ **AuthContext** : Gestion état authentification
- ✅ **ProtectedRoute** : Wrapper routes protégées
- ✅ **Token Refresh** : Automatique avant expiration
- ✅ **localStorage** : Stockage tokens
- ✅ **Axios interceptors** : Injection token automatique

#### Wizard 9 Étapes
- ✅ **Gestion État** : Hybride (localStorage + backend draft Job)
- ✅ **Composants** : `WizardContainer`, `WizardNavigation`, `WizardProgress`, `StepGroup`, `StepReleaseType`, `StepRules`, `StepFileSelection`, `StepAnalysis`, `StepEnrichment`, `StepTemplates`, `StepOptions`, `StepDestination`

### Backend

#### Structure Flask
- ✅ **Pattern** : Application Factory (`create_app()`)
- ✅ **Blueprints modulaires** : `auth.py`, `dashboard.py`, `wizard.py`, `releases.py`, `rules.py`, `users.py`, `roles.py`, `config.py`
- ✅ **Services métier** : `PackagingService`, `MetadataService`, `RuleService`, `TemplateService`, `FtpUploadService`, `JobService`, `AuthService`
- ⚠️ **Services critiques EBOOK** : `RuleParserService` (parse règle eBOOK [2022] complète), `RuleValidationService` (validation contre règle), `ScenerulesDownloadService` (téléchargement scenerules.org)
- ✅ **Règle eBOOK [2022] récupérée** : Document complet dans `docs/EBOOK_RULES_2022_COMPLETE.md` avec toutes spécifications (8 sections, formats, packaging, dirnaming)
- ✅ **Spécification packaging EBOOK** : `docs/PACKAGING_EBOOK_SPEC.md` avec processus complet conforme règle [2022]
- ✅ **ORM** : Flask-SQLAlchemy
- ✅ **Validation** : Marshmallow schemas
- ✅ **Auth** : Flask-JWT-Extended
- ✅ **Caching** : Flask-Caching

#### Base de Données
- ✅ **SGBD** : MySQL 8.0+ InnoDB
- ✅ **Migrations** : Flask-Migrate
- ✅ **Schéma complet** : 15 tables documentées (voir `docs/DATABASE_ERD.md`)
  - `users`, `roles`, `permissions`, `groups`
  - `user_groups`, `user_roles`, `role_permissions`, `user_permissions`
  - `releases`, `jobs`, `rules`
  - `api_configs`, `destinations`, `templates`, `preferences`
- ✅ **Relations** : Many-to-many (User↔Role, User↔Group, Role↔Permission), One-to-many (User→Release, Release→Job)

#### API REST
- ✅ **Documentation** : OpenAPI 3.0.3 (`docs/api/openapi.yaml` - 2 585 lignes)
- ✅ **Endpoints** : 64 endpoints documentés (Authentication, Dashboard, Wizard, Releases, Rules, Users, Roles, Configurations)
- ✅ **Format** : JSON
- ✅ **Authentification** : JWT Bearer Token
- ✅ **Permissions** : Vérification granulaire READ/WRITE/MOD/DELETE par ressource

### Décisions Techniques Critiques

#### v1 → v2 Migration
- ✅ **Approche** : **Tout refaire from scratch** en s'inspirant de v1 uniquement pour exemples
- ✅ **Code v1** : Utilisé uniquement comme référence, pas de réutilisation directe
- ✅ **Base de données** : Nouvelle base v2, pas de migration données

#### TypeScript
- ✅ **Décision** : **TypeScript dès le début** (pas de migration progressive)
- ✅ **Configuration** : Mode strict activé

#### Templates NFO
- ✅ **Format** : Format v1 avec placeholders `{{variable}}` et conditionnelles `{% if %}`
- ✅ **Améliorations** : Placeholders progressifs selon output métadonnées/mediainfo (ajout au fur et à mesure des tests)
- ✅ **Stockage** : Disque OU base de données (choix configurable)
- ✅ **Édition** : Inline avec visualisation "nfo viewer" monospace UTF-8
- ✅ **Prévisualisation** : Temps réel avec "nfo viewer" monospace UTF-8

#### Sécurité
- ✅ **Chiffrement credentials** : Fernet (API keys, FTP passwords)
- ✅ **Permissions granulaire** : Model `Permission` avec `resource` et `action` (READ/WRITE/MOD/DELETE)
- ✅ **Validation** : Input validation stricte partout

#### Tests
- ✅ **Méthodologie** : TDD strict (Red-Green-Refactor)
- ✅ **Tests E2E** : **Playwright MCP obligatoire** (pas Playwright standard)
- ✅ **Couverture** : 100% requis pour merge
- ✅ **Structure** : `tests/unit/`, `tests/integration/`, `tests/e2e/`

### Production

#### Infrastructure
- ✅ **Serveur** : Dédié Debian 12
- ✅ **Conteneurisation** : Docker/Docker Compose
- ✅ **Web Server** : Nginx + Gunicorn ou uWSGI (dans Docker)
- ✅ **Process Manager** : Supervisor (dans Docker)
- ✅ **Monitoring** : Prometheus + Grafana
- ✅ **Logs** : ELK stack + fichiers logs

#### CI/CD
- ✅ **Pipeline** : GitHub Actions
- ✅ **Tests automatiques** : Tous tests passent en CI
- ✅ **Coverage check** : ≥90% requis

### Documentation Créée

- ✅ **CDC** : `docs/cdc.md` (Cahier des Charges complet)
- ✅ **PRDs** : PRD-001 à PRD-007 (tous créés)
- ✅ **Database ERD** : `docs/DATABASE_ERD.md` (schéma complet avec relations)
- ✅ **API Reference** : `docs/API_REFERENCE.md` + `docs/api/openapi.yaml` (OpenAPI 3.0.3)
- ✅ **Vite Setup** : `docs/VITE_SETUP.md` (configuration complète React+TypeScript)
- ✅ **MCP Tools Guide** : `docs/MCP_TOOLS_GUIDE.md`
- ⚠️ **Scenerules Integration** : `docs/SCENERULES_INTEGRATION.md` (CRITIQUE - connaissance totale règles scenerules.org obligatoire pour EBOOK)

### Références Techniques

- **Vite Configuration** : `docs/VITE_SETUP.md`
- **Database Schema** : `docs/DATABASE_ERD.md`
- **API Documentation** : `docs/api/openapi.yaml` (Swagger UI compatible)
- **Project Analysis** : `docs/PROJECT_ANALYSIS_QUESTIONS.md` (décisions détaillées)

---

## 📊 Résumé des Progrès

### Statistiques Globales
- **Phases complétées** : 1 / 9 ✅ (Phase 0 à 100%)
- **Étapes complétées** : 5 / 67 ✅ (Phase 0 complète)
- **Tâches complétées** : ~50+ / 245
- **Tests écrits** : 35 (33 Phase 0 + 2 exemples)
- **Couverture de tests** : 100% (Phase 0) ✅

### Prochaines Priorités (Matrice Eisenhower)
- **Urgent & Important** : Phase 0 - Préparation
- **Important, pas urgent** : Phase 1 - Infrastructure Core
- **Urgent, pas important** : Configuration environnement
- **Ni urgent ni important** : Optimisations futures

---

## 🎯 OKRs (Objectives and Key Results)

### OKR Global Q4 2025
**Objectif** : Livrer une v2 fonctionnelle avec architecture propre et tests complets

**Key Results** :
- [ ] 100% des fonctionnalités principales implémentées
- [ ] 100% de couverture de tests
- [ ] Documentation complète et à jour
- [ ] Déploiement réussi en production

### OKR Phase 0 - Préparation
**Objectif** : Préparer l'environnement de développement et la documentation

**Key Results** :
- [x] Backup v1/ complété ✅
- [x] Tous les fichiers de documentation créés ✅
- [x] Environnement TDD configuré ✅
- [x] Règles Cursor créées ✅
- [x] Décisions architecturales documentées ✅
- [x] PRDs complets créés (PRD-002 à PRD-007) ✅
- [x] Database ERD créé ✅
- [x] API OpenAPI/Swagger créée ✅
- [x] Configuration Vite recherchée et documentée ✅

**Statut** : ✅ **TERMINÉ À 100%**

---

## 📋 Phases du Projet

### Phase 0 : Préparation ✅

**Statut** : ✅ **COMPLÉTÉE À 100%**  
**Priorité MoSCoW** : Must Have  
**Date début** : 2025-11-01  
**Date fin** : 2025-11-01  
**Couverture tests** : 100% ✅

#### Validation Phase 0

- ✅ **Toutes étapes complétées à 100%**
- ✅ **Tests Phase 0** : 33 tests, tous passent (100%)
- ✅ **Couverture** : 100% (tests de validation)
- ✅ **Documentation** : Complète et à jour
- ✅ **Definition of Done** : Tous critères satisfaits

#### Étapes

##### Étape 0.1 : Backup v1/ ✅
- **Description** : Créer backup complet du codebase actuel dans v1/
- **Critères de validation** :
  - ✅ Tous les fichiers/dossiers copiés dans v1/
  - ✅ Structure préservée
  - ✅ Structure racine correcte
- **Tests nécessaires** : ✅ Tests validation passent (3/3)
- **Statut** : ✅ **Terminée à 100%**

##### Étape 0.2 : Création Documentation Structurée ✅
- **Description** : Créer tous les fichiers de documentation (CDC, DEVBOOK, PRDs, etc.)
- **Critères de validation** :
  - ✅ docs/cdc.md créé et complet (15KB)
  - ✅ docs/DEVBOOK.md créé (ce fichier)
  - ✅ docs/todolist.md créé avec découpage détaillé (15KB)
  - ✅ docs/PRDs/ avec README et PRD-001
  - ✅ docs/BACKLOG_AGILE.md créé
  - ✅ docs/PROJECT_OVERVIEW.md créé
  - ✅ docs/TEST_PLAN.md créé
  - ✅ docs/RISKS_REGISTER.md créé
  - ✅ docs/DEPLOYMENT_PLAN.md créé
  - ✅ docs/MCP_TOOLS_GUIDE.md créé
- **Tests nécessaires** : ✅ Tests validation passent (10/10)
- **Statut** : ✅ **Terminée à 100%**

##### Étape 0.3 : Configuration Environnement Développement ✅
- **Description** : Setup environnement développement (venv, dépendances, etc.)
- **Critères de validation** :
  - ✅ Environnement virtuel Python configuré (Python 3.11.2)
  - ✅ requirements.txt et requirements-dev.txt créés
  - ✅ Dépendances installées
  - ✅ pytest.ini et .coveragerc configurés
- **Tests nécessaires** : ✅ Tests validation passent (4/4)
- **Statut** : ✅ **Terminée à 100%**

##### Étape 0.4 : Setup TDD ✅
- **Description** : Configuration outils de tests (pytest, coverage, etc.)
- **Critères de validation** :
  - ✅ pytest installé et configuré
  - ✅ pytest-cov configuré
  - ✅ Structure tests/ créée (unit/, integration/, e2e/)
  - ✅ Fixtures de base créées (conftest.py)
  - ✅ Tests exemples passent
- **Tests nécessaires** : ✅ Tests validation passent (4/4)
- **Statut** : ✅ **Terminée à 100%**

##### Étape 0.5 : Règles Cursor ✅
- **Description** : Créer toutes les règles Cursor dans .cursor/rules/
- **Critères de validation** :
  - ✅ .cursor/rules/project-v2.mdc créé (avec MCP Tools et Definition of Done)
  - ✅ .cursor/rules/tdd-methodology.mdc créé (avec Definition of Done)
  - ✅ .cursor/rules/mcp-tools-usage.mdc créé (nouveau)
  - ✅ .cursor/rules/documentation-standards.mdc créé
  - ✅ .cursor/rules/testing-requirements.mdc créé
  - ✅ .cursor/rules/definition-of-done.mdc créé (nouveau - CRITIQUE)
  - ✅ .cursor/RULES_ATTACHMENT_GUIDE.md créé
- **Tests nécessaires** : ✅ Tests validation passent (7/7)
- **Statut** : ✅ **Terminée à 100%**

---

### Phase 1 : Infrastructure Core ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Date début estimée** : 2025-11-08  
**Date fin estimée** : 2025-11-22

#### Étapes

##### Étape 1.1 : Setup Flask App Factory
- **Description** : Créer structure Flask avec application factory pattern
- **Critères de validation** :
  - web/app.py avec create_app()
  - Configuration par environnement (.env)
  - Blueprints structure prête
- **Tests nécessaires** :
  - Test création app
  - Test configuration par environnement
- **Statut** : ⏳ Non commencée

##### Étape 1.2 : Base de Données MySQL
- **Description** : Setup MySQL avec Flask-SQLAlchemy
- **Critères de validation** :
  - Connexion DB fonctionnelle
  - Models de base créés
  - Flask-Migrate configuré
- **Tests nécessaires** :
  - Test connexion DB
  - Test création tables
- **Statut** : ⏳ Non commencée

##### Étape 1.3 : Authentification JWT
- **Description** : Implémenter authentification JWT avec Flask-JWT-Extended
- **Critères de validation** :
  - Login fonctionnel
  - Token refresh
  - Révocation tokens
- **Tests nécessaires** :
  - Test login
  - Test refresh token
  - Test protection routes
- **Statut** : ⏳ Non commencée

##### Étape 1.4 : Modèles de Base
- **Description** : Créer modèles User, Role, Permission, Group
- **Critères de validation** :
  - Modèles créés avec relations
  - Migrations générées
  - Tests CRUD passent
- **Tests nécessaires** :
  - Tests création/modification/suppression
  - Tests relations
- **Statut** : ⏳ Non commencée

**Voir** : `docs/todolist.md` pour détails complets de toutes les sous-étapes.

---

### Phase 2 : Interface Administration ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 1  
**Date début estimée** : 2025-11-22  
**Date fin estimée** : 2025-12-13

#### Étapes

##### Étape 2.1 : Dashboard
##### Étape 2.2 : Navigation
##### Étape 2.3 : Structure Pages
##### Étape 2.4 : Thème Jour/Nuit

**Voir** : `docs/todolist.md` pour détails complets.

---

### Phase 3 : Nouvelle Release Wizard ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 1, Phase 2  
**Date début estimée** : 2025-12-13  
**Date fin estimée** : 2026-01-10

**⚠️ PRÉREQUIS CRITIQUE** : Avant de commencer Phase 3, la règle **[2022] eBOOK** de https://scenerules.org/ DOIT être analysée intégralement et le `RuleParserService` implémenté pour garantir packaging conforme 100%.

**Voir** : 
- `docs/PREREQUISITES_PHASE3_WIZARD.md` pour prérequis obligatoires
- `docs/SCENE_RULES_EBOOK_ANALYSIS.md` pour analyse complète des règles
- `docs/PRDs/PRD-002-Nouvelle-Release.md` pour détails fonctionnels

#### Étapes

##### Étape 3.1 : Étapes 1-3 (Groupe, Type, Règle)
##### Étape 3.2 : Étapes 4-5 (Fichier, Analyse)
##### Étape 3.3 : Étapes 6-7 (Enrichissement, Templates)
##### Étape 3.4 : Étapes 8-9 (Packaging, Destination)

---

### Phase 4 : Liste des Releases ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 3  
**Date début estimée** : 2026-01-10  
**Date fin estimée** : 2026-01-24

**Voir** : `docs/PRDs/PRD-003-Liste-Releases.md` pour détails.

---

### Phase 5 : Rules Management ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 1  
**Date début estimée** : 2026-01-24  
**Date fin estimée** : 2026-02-14

**Voir** : `docs/PRDs/PRD-004-Rules.md` pour détails.

---

### Phase 6 : Utilisateurs & Rôles ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 1  
**Date début estimée** : 2026-02-14  
**Date fin estimée** : 2026-02-28

**Voir** : `docs/PRDs/PRD-005-Utilisateurs.md` et `docs/PRDs/PRD-006-Roles.md` pour détails.

---

### Phase 7 : Configurations ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 1  
**Date début estimée** : 2026-02-28  
**Date fin estimée** : 2026-03-14

**Voir** : `docs/PRDs/PRD-007-Configurations.md` pour détails.

---

### Phase 8 : Tests & Optimisation ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Toutes phases précédentes  
**Date début estimée** : 2026-03-14  
**Date fin estimée** : 2026-03-28

#### Étapes

##### Étape 8.1 : Tests E2E Complets
##### Étape 8.2 : Optimisation Performance
##### Étape 8.3 : Accessibilité WCAG 2.2 AA

---

### Phase 9 : Déploiement ⏳

**Statut** : ⏳ Non commencée  
**Priorité MoSCoW** : Must Have  
**Dépendances** : Phase 8  
**Date début estimée** : 2026-03-28  
**Date fin estimée** : 2026-04-04

**Voir** : `docs/DEPLOYMENT_PLAN.md` pour détails.

---

## 📝 Journal des Modifications

| Date | Phase | Étape | Action | Auteur |
|------|-------|-------|--------|--------|
| 2025-11-01 | Phase 0 | 0.1 | Backup v1/ créé | Dev Team |
| 2025-11-01 | Phase 0 | 0.2 | Documentation structurée créée | Dev Team |
| 2025-11-01 | Phase 0 | 0.2 | PRD-002 à PRD-007 créés (Wizard, Releases, Rules, Users, Roles, Config) | Dev Team |
| 2025-11-01 | Phase 0 | 0.2 | Database ERD créé (15 tables, relations complètes) | Dev Team |
| 2025-11-01 | Phase 0 | 0.2 | API OpenAPI/Swagger créée (64 endpoints, 2 585 lignes) | Dev Team |
| 2025-11-01 | Phase 0 | 0.2 | Configuration Vite documentée (React+TypeScript) | Dev Team |
| 2025-11-01 | Phase 0 | - | Décisions architecturales documentées dans DEVBOOK | Dev Team |

---

## 🔗 Liens Utiles

- **CDC** : `docs/cdc.md`
- **TodoList** : `docs/todolist.md`
- **PRDs** : `docs/PRDs/`
- **Backlog** : `docs/BACKLOG_AGILE.md`
- **Test Plan** : `docs/TEST_PLAN.md`
- **Risks** : `docs/RISKS_REGISTER.md`
- **Deployment** : `docs/DEPLOYMENT_PLAN.md`

---

**Dernière mise à jour** : 2025-11-01  
**Prochaine révision** : À chaque étape complétée

---

## ✅ Vérification Règles

**Date** : 2025-11-01

### Règles Respectées ✅

1. **Definition of Done** ✅
   - Documentation complète et à jour
   - Pas de code production écrit sans tests
   - Tous critères satisfaits

2. **TDD Methodology** ✅
   - Tests E2E mentionnés dans tous PRDs (Playwright MCP)
   - Aucun code écrit sans tests correspondants

3. **MCP Tools Usage** ✅
   - Context7 MCP utilisé pour recherche Vite
   - Playwright MCP mentionné dans tous PRDs
   - Documentation intégrée

4. **Documentation Standards** ✅
   - Format OpenAPI 3.0.3 standardisé
   - Structure cohérente avec liens croisés
   - Guide d'utilisation créé

5. **Project v2 Guidelines** ✅
   - Vite confirmé et documenté
   - TypeScript dès le début
   - Architecture modulaire respectée

**Voir** : `docs/RULES_VERIFICATION.md` pour détails complets

