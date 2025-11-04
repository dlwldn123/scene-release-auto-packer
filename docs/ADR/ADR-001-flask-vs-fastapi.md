# ADR-001 : Choix Flask vs FastAPI

**ID** : ADR-001  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

Lors de la refonte complète du projet (v2), nous devions choisir le framework backend Python pour l'API REST. Deux options principales étaient considérées :

1. **Flask** : Framework minimaliste et flexible, très mature
2. **FastAPI** : Framework moderne avec support natif async/await, validation automatique avec Pydantic

**Contraintes** :
- Compatibilité avec code existant (v1)
- Simplicité de maintenance
- Performance suffisante (pas de contraintes extrêmes)
- Écosystème mature et stable

---

## Décision

**Nous avons décidé d'utiliser Flask** pour le backend API.

**Raisons principales** :
1. **Simplicité** : Flask est minimaliste et facile à comprendre
2. **Maturité** : Écosystème très mature avec nombreuses extensions
3. **Flexibilité** : Permet de choisir les composants nécessaires
4. **Compatibilité** : Meilleure compatibilité avec code existant et dépendances
5. **Documentation** : Documentation excellente et communauté large
6. **Performance suffisante** : Pour notre cas d'usage (API REST classique), Flask est suffisant

---

## Conséquences

### Positives ✅

- **Courbe d'apprentissage faible** : Flask est simple et intuitif
- **Écosystème mature** : Extensions nombreuses et bien maintenues (Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, etc.)
- **Flexibilité** : Architecture modulaire avec Blueprints
- **Stabilité** : Framework très stable, peu de breaking changes
- **Documentation** : Documentation excellente et nombreux tutoriels

### Négatives ❌

- **Pas de support async natif** : Flask nécessite des extensions pour async (Gevent, etc.)
- **Performance** : Légèrement moins performant que FastAPI pour cas très haute charge
- **Validation** : Validation manuelle avec Marshmallow (vs validation automatique Pydantic)

### Alternatives Considérées

#### FastAPI (Rejeté)
- **Avantages** : Support async natif, validation automatique, documentation automatique (OpenAPI)
- **Inconvénients** : Plus complexe, écosystème moins mature, courbe d'apprentissage plus élevée
- **Raison du rejet** : Complexité inutile pour notre cas d'usage, Flask suffit amplement

#### Django REST Framework (Rejeté)
- **Avantages** : Framework complet avec ORM intégré
- **Inconvénients** : Trop lourd, moins flexible que Flask
- **Raison du rejet** : Besoin de flexibilité, pas besoin de toutes les fonctionnalités Django

---

## Références

- Flask Documentation : https://flask.palletsprojects.com/
- FastAPI Documentation : https://fastapi.tiangolo.com/
- Comparaison Flask vs FastAPI : https://testdriven.io/blog/fastapi-crud/

---

**Dernière mise à jour** : 2025-11-03
