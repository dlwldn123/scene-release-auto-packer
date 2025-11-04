# ADR-003 : Choix MySQL vs PostgreSQL

**ID** : ADR-003  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

Pour la base de données du projet, nous devions choisir entre MySQL et PostgreSQL. Les deux sont des bases de données relationnelles open-source très populaires.

**Contraintes** :
- Compatibilité avec SQLAlchemy
- Performance pour cas d'usage standard
- Facilité de déploiement et maintenance
- Support transactions et relations complexes

---

## Décision

**Nous avons décidé d'utiliser MySQL** pour la base de données.

**Raisons principales** :
1. **Simplicité** : MySQL est plus simple à configurer et maintenir
2. **Performance** : Excellente performance pour cas d'usage standard (lecture/écriture)
3. **Compatibilité** : Très bon support SQLAlchemy
4. **Ecosystème** : Large écosystème d'outils et hébergements disponibles
5. **Stabilité** : Très stable et mature

---

## Conséquences

### Positives ✅

- **Simplicité** : Configuration et maintenance simples
- **Performance** : Excellente performance pour notre cas d'usage
- **Compatibilité** : Support SQLAlchemy excellent
- **Déploiement** : Facile de déployer (Docker, cloud providers)

### Négatives ❌

- **Fonctionnalités avancées** : Moins de fonctionnalités avancées que PostgreSQL (JSON, arrays, etc.)
- **Standards SQL** : Moins strict sur standards SQL que PostgreSQL

### Alternatives Considérées

#### PostgreSQL (Rejeté)
- **Avantages** : Plus de fonctionnalités avancées, meilleur support standards SQL
- **Inconvénients** : Plus complexe, légèrement moins performant pour cas simples
- **Raison du rejet** : Complexité inutile pour notre cas d'usage, MySQL suffit amplement

---

## Références

- MySQL Documentation : https://dev.mysql.com/doc/
- PostgreSQL Documentation : https://www.postgresql.org/docs/
- SQLAlchemy MySQL Support : https://docs.sqlalchemy.org/en/20/dialects/mysql.html

---

**Dernière mise à jour** : 2025-11-03
