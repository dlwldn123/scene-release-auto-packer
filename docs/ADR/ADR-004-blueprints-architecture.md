# ADR-004 : Architecture Blueprints Modulaires

**ID** : ADR-004  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

Pour organiser le code backend Flask, nous devions choisir une architecture modulaire. Plusieurs approches étaient possibles :

1. **Blueprints Flask** : Système de modules natif Flask
2. **Monolithe** : Tout dans `app.py`
3. **Packages séparés** : Applications Flask séparées

**Contraintes** :
- Maintenabilité du code
- Séparation des responsabilités
- Facilité de test
- Scalabilité future

---

## Décision

**Nous avons décidé d'utiliser l'architecture Blueprints modulaires** pour organiser le code backend.

**Structure** :
```
web/
├── app.py                 # Application factory
├── blueprints/
│   ├── auth.py           # Authentification
│   ├── dashboard.py      # Dashboard
│   ├── wizard.py          # Wizard 9 étapes
│   ├── releases.py        # Releases management
│   ├── rules.py           # Rules management
│   └── ...
├── models/                # SQLAlchemy models
├── services/              # Services métier
└── utils/                 # Utilitaires
```

**Raisons principales** :
1. **Modularité** : Chaque blueprint est indépendant et réutilisable
2. **Séparation des responsabilités** : Chaque blueprint gère un domaine fonctionnel
3. **Maintenabilité** : Code organisé et facile à maintenir
4. **Tests** : Facile de tester chaque blueprint indépendamment
5. **Scalabilité** : Facile d'ajouter de nouveaux blueprints

---

## Conséquences

### Positives ✅

- **Modularité** : Code organisé par domaine fonctionnel
- **Maintenabilité** : Facile de trouver et modifier code
- **Tests** : Tests isolés par blueprint
- **Réutilisabilité** : Blueprints réutilisables dans d'autres projets
- **Scalabilité** : Facile d'ajouter de nouvelles fonctionnalités

### Négatives ❌

- **Complexité initiale** : Légèrement plus complexe qu'un monolithe simple
- **Navigation** : Plus de fichiers à naviguer (mais mieux organisé)

### Alternatives Considérées

#### Monolithe (Rejeté)
- **Avantages** : Plus simple, tout au même endroit
- **Inconvénients** : Difficile à maintenir, code spaghetti, pas scalable
- **Raison du rejet** : Pas scalable, difficile à maintenir pour projet de taille moyenne

#### Applications Flask Séparées (Rejeté)
- **Avantages** : Isolation complète entre applications
- **Inconvénients** : Complexité inutile, partage de modèles difficile
- **Raison du rejet** : Complexité inutile pour notre cas d'usage

---

## Références

- Flask Blueprints Documentation : https://flask.palletsprojects.com/en/2.3.x/blueprints/
- Application Factory Pattern : https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/

---

**Dernière mise à jour** : 2025-11-03
