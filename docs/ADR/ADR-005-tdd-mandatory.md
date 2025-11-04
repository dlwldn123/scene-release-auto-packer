# ADR-005 : TDD Obligatoire

**ID** : ADR-005  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

Pour garantir la qualité du code et réduire les bugs, nous devions choisir une approche de tests. Plusieurs approches étaient possibles :

1. **TDD (Test-Driven Development)** : Tests avant code
2. **Tests après code** : Code d'abord, tests ensuite
3. **Pas de tests** : Seulement tests manuels

**Contraintes** :
- Qualité du code
- Réduction des bugs
- Maintenabilité
- Couverture de code ≥90%

---

## Décision

**Nous avons décidé d'adopter le TDD (Test-Driven Development) comme pratique obligatoire** pour tout développement.

**Règles strictes** :
1. **Toujours écrire les tests avant le code** (cycle Red-Green-Refactor)
2. **Couverture minimale 90%** (idéal 100%)
3. **Tests unitaires** pour toutes les fonctions/méthodes
4. **Tests d'intégration** pour les interactions entre composants
5. **Tests E2E** pour les flux utilisateur complets
6. **Aucun code ne peut être mergé sans tests correspondants**

---

## Conséquences

### Positives ✅

- **Qualité code** : Code de meilleure qualité, moins de bugs
- **Confiance** : Confiance dans les modifications futures
- **Documentation** : Tests servent de documentation du comportement
- **Refactoring** : Refactoring sécurisé grâce aux tests
- **Couverture** : Couverture de code élevée (95% actuellement)

### Négatives ❌

- **Temps développement** : Plus de temps pour écrire les tests
- **Courbe d'apprentissage** : Nécessite discipline et formation
- **Maintenance** : Maintenance des tests en plus du code

### Alternatives Considérées

#### Tests Après Code (Rejeté)
- **Avantages** : Plus rapide initialement
- **Inconvénients** : Tests souvent incomplets ou oubliés, moins de confiance
- **Raison du rejet** : Ne garantit pas la qualité, tests souvent incomplets

#### Pas de Tests (Rejeté)
- **Avantages** : Développement plus rapide initialement
- **Inconvénients** : Bugs nombreux, refactoring risqué, maintenance difficile
- **Raison du rejet** : Inacceptable pour projet de qualité

---

## Références

- TDD Methodology : `.cursor/rules/tdd-methodology.mdc`
- Testing Requirements : `.cursor/rules/testing-requirements.mdc`
- Test Plan : `docs/TEST_PLAN.md`

---

**Dernière mise à jour** : 2025-11-03
