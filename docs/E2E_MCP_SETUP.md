# Migration Tests E2E - Setup Guide

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Ce guide explique comment mettre en place Playwright Browser MCP pour les tests E2E.

---

## 📋 Prérequis

### 1. Installer Playwright Browser MCP Server

```bash
# Installer le serveur MCP Playwright Browser
npm install -g @modelcontextprotocol/server-playwright-browser
```

### 2. Configurer Cursor/MCP

Ajouter la configuration MCP dans votre configuration Cursor :

```json
{
  "mcpServers": {
    "playwright-browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-playwright-browser"
      ]
    }
  }
}
```

### 3. Démarrer Serveur MCP

```bash
# Démarrer le serveur MCP (si nécessaire)
npx @modelcontextprotocol/server-playwright-browser
```

---

## 🔄 Migration des Tests

### Pattern de Migration

**Ancien (Playwright Standard)** :
```python
def test_login(page: Page):
    page.goto("http://localhost:8080/login")
    page.fill('input[name="username"]', "admin")
    page.click('button[type="submit"]')
```

**Nouveau (Playwright Browser MCP)** :
```python
def test_login_mcp():
    # Navigation
    mcp_playwright_browser_navigate(url="http://localhost:8080/login")
    
    # Capturer état
    snapshot = mcp_playwright_browser_snapshot()
    assert "Login" in snapshot
    
    # Interagir
    mcp_playwright_browser_type(
        element="username input",
        ref="input[name='username']",
        text="admin"
    )
    mcp_playwright_browser_click(
        element="login button",
        ref="button[type='submit']"
    )
    
    # Attendre résultat
    mcp_playwright_browser_wait_for(text="Dashboard")
```

---

## ✅ Tests Migrés

### Fichiers Créés

- ✅ `tests/e2e/phase8/test_e2e_flows_mcp.py` : Tests E2E avec pattern MCP

### État Migration

- ✅ Pattern de migration documenté
- ✅ Exemples de tests créés
- ⏳ Migration complète nécessite serveur MCP opérationnel

---

## 📝 Notes

**Important** : Les tests MCP sont actuellement marqués `@pytest.mark.skip` car ils nécessitent un serveur MCP configuré et démarré.

**Pour activer les tests** :
1. Installer et configurer Playwright Browser MCP Server
2. Retirer `@pytest.mark.skip` des tests
3. Adapter les appels MCP selon votre configuration

---

## 🔗 Références

- MCP Tools Guide : `docs/MCP_TOOLS_GUIDE.md`
- E2E Migration Guide : `docs/E2E_MIGRATION_GUIDE.md`
- ADR-007 : `docs/ADR/ADR-007-playwright-browser-mcp.md`

---

**Dernière mise à jour** : 2025-11-03
