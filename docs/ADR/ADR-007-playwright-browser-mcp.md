# ADR-007 : Playwright Browser MCP pour Tests E2E

**ID** : ADR-007  
**Date** : 2025-11-03  
**Statut** : ✅ Accepted  
**Décideurs** : Équipe de développement

---

## Contexte

Pour les tests E2E (End-to-End), nous devions choisir l'outil de test. Plusieurs options étaient possibles :

1. **Playwright Browser MCP** : Outil MCP (Model Context Protocol) pour tests E2E
2. **Playwright Standard** : Playwright classique avec API Python/JavaScript
3. **Selenium** : Outil classique pour tests E2E

**Contraintes** :
- Intégration avec workflow de développement
- Productivité et vitesse d'écriture
- Fiabilité des tests
- Documentation et support

---

## Décision

**Nous avons décidé d'utiliser Playwright Browser MCP Tools** pour tous les tests E2E.

**Raisons principales** :
1. **Productivité** : Tests E2E plus rapides à écrire avec MCP Tools
2. **Intégration** : Intégration native avec workflow de développement
3. **Fiabilité** : Tests plus fiables et maintenables
4. **Documentation** : Documentation intégrée dans outils MCP
5. **Standardisation** : Utilisation standardisée des outils MCP dans le projet

**Règles strictes** :
- ✅ **Toujours utiliser Playwright Browser MCP** pour tests E2E
- ❌ **JAMAIS utiliser Playwright standard** si MCP disponible
- ✅ Utiliser `mcp_playwright_browser_navigate`, `mcp_playwright_browser_snapshot`, etc.

---

## Conséquences

### Positives ✅

- **Productivité** : Tests E2E plus rapides à écrire
- **Intégration** : Intégration native avec workflow développement
- **Fiabilité** : Tests plus fiables et maintenables
- **Standardisation** : Utilisation standardisée des outils MCP

### Négatives ❌

- **Courbe d'apprentissage** : Nécessite familiarisation avec MCP Tools
- **Dépendance** : Dépendance aux outils MCP (mais standardisé)

### Alternatives Considérées

#### Playwright Standard (Rejeté)
- **Avantages** : API familière, nombreux exemples
- **Inconvénients** : Moins productif, moins intégré avec workflow
- **Raison du rejet** : Moins productif, moins intégré

#### Selenium (Rejeté)
- **Avantages** : Outil classique et mature
- **Inconvénients** : Moins performant, API moins moderne
- **Raison du rejet** : Moins performant et moderne que Playwright

---

## Références

- MCP Tools Guide : `docs/MCP_TOOLS_GUIDE.md`
- Playwright Browser MCP Documentation : `.cursor/rules/mcp-tools-usage.mdc`
- TDD Methodology : `.cursor/rules/tdd-methodology.mdc`

---

**Dernière mise à jour** : 2025-11-03
