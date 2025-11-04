# ADR-006 : Migration SQLAlchemy 2.0 API

**ID** : ADR-006  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

SQLAlchemy 2.0 introduit une nouvelle API moderne (Core + ORM unifiés) avec des améliorations de performance et de type safety. Nous devions choisir entre :

1. **SQLAlchemy 2.0 API** : Nouvelle API moderne avec type hints
2. **SQLAlchemy 1.4 Legacy API** : API classique (backward compatible)

**Contraintes** :
- Compatibilité avec code existant
- Performance
- Type safety avec TypeScript/Python
- Maintenabilité future

---

## Décision

**Nous avons décidé d'utiliser la nouvelle API SQLAlchemy 2.0** pour tous les nouveaux développements.

**Raisons principales** :
1. **Type Safety** : Meilleur support des type hints Python
2. **Performance** : Améliorations de performance significatives
3. **Modernité** : API moderne et plus intuitive
4. **Future-proof** : API recommandée pour l'avenir
5. **Compatibilité** : Compatible avec SQLAlchemy 1.4 via mode legacy

**Migration progressive** :
- Nouveau code : API 2.0 uniquement
- Code existant : Migration progressive vers API 2.0

---

## Conséquences

### Positives ✅

- **Type Safety** : Meilleur support des type hints
- **Performance** : Améliorations de performance
- **Modernité** : API plus moderne et intuitive
- **Future-proof** : API recommandée pour l'avenir

### Négatives ❌

- **Courbe d'apprentissage** : Légère courbe d'apprentissage pour nouvelle API
- **Migration** : Nécessite migration progressive du code existant

### Alternatives Considérées

#### SQLAlchemy 1.4 Legacy API (Rejeté)
- **Avantages** : API familière, pas de migration nécessaire
- **Inconvénients** : API dépréciée, moins performante, moins de type safety
- **Raison du rejet** : Pas future-proof, moins performant

---

## Références

- SQLAlchemy 2.0 Documentation : https://docs.sqlalchemy.org/en/20/
- Migration Guide : https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
- SQLAlchemy 2.0 Tutorial : https://docs.sqlalchemy.org/en/20/tutorial/

---

**Dernière mise à jour** : 2025-11-03
