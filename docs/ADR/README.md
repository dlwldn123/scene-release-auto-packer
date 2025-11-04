# Architecture Decision Records (ADR)

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 📋 Vue d'Ensemble

Les **Architecture Decision Records (ADR)** documentent les décisions architecturales importantes prises lors du développement du projet eBook Scene Packer v2.

### Format Standard

Chaque ADR suit le format suivant :

```markdown
# ADR-XXX : Titre de la Décision

**ID** : ADR-XXX
**Date** : YYYY-MM-DD
**Statut** : Proposed | Accepted | Deprecated | Superseded
**Décideurs** : Équipe de développement

## Contexte

[Contexte qui a nécessité cette décision]

## Décision

[Nous avons décidé de...]

## Conséquences

### Positives
- [Avantages de la décision]

### Négatives
- [Inconvénients de la décision]

### Alternatives Considérées
- [Alternatives évaluées et pourquoi elles ont été rejetées]
```

---

## 📚 Liste des ADR

### ADR-001 : Choix Flask vs FastAPI
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-001-flask-vs-fastapi.md`

### ADR-002 : Choix React 19 vs Vue 3
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-002-react-vs-vue.md`

### ADR-003 : Choix MySQL vs PostgreSQL
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-003-mysql-vs-postgresql.md`

### ADR-004 : Architecture Blueprints Modulaires
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-004-blueprints-architecture.md`

### ADR-005 : TDD Obligatoire
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-005-tdd-mandatory.md`

### ADR-006 : Migration SQLAlchemy 2.0 API
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-006-sqlalchemy-2.0.md`

### ADR-007 : Playwright Browser MCP pour Tests E2E
**Statut** : ✅ Accepted  
**Date** : 2025-11-03  
**Voir** : `docs/ADR/ADR-007-playwright-browser-mcp.md`

---

## 📝 Template ADR

Pour créer un nouvel ADR, copier `docs/ADR/TEMPLATE.md` et suivre le format standard.

---

**Dernière mise à jour** : 2025-11-03  
**Mainteneur** : Équipe de développement
