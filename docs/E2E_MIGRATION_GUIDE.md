# Guide Migration Tests E2E vers Playwright Browser MCP

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Ce guide explique comment migrer les tests E2E existants de Playwright standard vers **Playwright Browser MCP Tools**.

---

## ❌ Ancienne Méthode (Playwright Standard)

```python
from playwright.sync_api import Page, expect

def test_login_flow_e2e(page: Page) -> None:
    """Test login flow avec Playwright standard."""
    # Navigation
    page.goto("http://localhost:8080/login")
    
    # Attendre éléments
    expect(page.locator('input[name="username"]')).toBeVisible()
    
    # Remplir formulaire
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "password")
    
    # Cliquer
    page.click('button[type="submit"]')
    
    # Vérifier redirection
    expect(page).toHaveURL("http://localhost:8080/dashboard")
```

---

## ✅ Nouvelle Méthode (Playwright Browser MCP)

```python
def test_login_flow_e2e_mcp() -> None:
    """Test login flow avec Playwright Browser MCP."""
    # 1. Navigation
    mcp_playwright_browser_navigate(url="http://localhost:8080/login")
    
    # 2. Capturer état initial
    snapshot = mcp_playwright_browser_snapshot()
    assert "Login" in snapshot
    
    # 3. Interagir avec formulaire
    mcp_playwright_browser_type(
        element="username input",
        ref="input[name='username']",
        text="admin"
    )
    mcp_playwright_browser_type(
        element="password input",
        ref="input[name='password']",
        text="password"
    )
    
    # 4. Cliquer bouton
    mcp_playwright_browser_click(
        element="login button",
        ref="button[type='submit']"
    )
    
    # 5. Attendre redirection
    mcp_playwright_browser_wait_for(text="Dashboard")
    
    # 6. Vérifier résultat
    final_snapshot = mcp_playwright_browser_snapshot()
    assert "Dashboard" in final_snapshot
```

---

## 🔄 Mapping Actions

### Navigation

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `page.goto(url)` | `mcp_playwright_browser_navigate(url=url)` |

### Attendre Éléments

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `expect(page.locator(...)).toBeVisible()` | `mcp_playwright_browser_wait_for(ref="...")` |

### Remplir Formulaire

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `page.fill('input[name="username"]', "admin")` | `mcp_playwright_browser_type(element="username input", ref="input[name='username']", text="admin")` |

### Cliquer

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `page.click('button[type="submit"]')` | `mcp_playwright_browser_click(element="submit button", ref="button[type='submit']")` |

### Vérifier URL

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `expect(page).toHaveURL(url)` | `snapshot = mcp_playwright_browser_snapshot(); assert url in snapshot` |

### Screenshot

| Ancien (Playwright Standard) | Nouveau (Playwright Browser MCP) |
|------------------------------|----------------------------------|
| `page.screenshot(path="screenshot.png")` | `mcp_playwright_browser_take_screenshot(filename="screenshot.png")` |

---

## 📋 Checklist Migration

### Pour Chaque Test E2E

- [ ] Remplacer `page.goto()` par `mcp_playwright_browser_navigate()`
- [ ] Remplacer `page.fill()` par `mcp_playwright_browser_type()`
- [ ] Remplacer `page.click()` par `mcp_playwright_browser_click()`
- [ ] Remplacer `expect(...).toBeVisible()` par `mcp_playwright_browser_wait_for()`
- [ ] Remplacer `expect(page).toHaveURL()` par vérification snapshot
- [ ] Remplacer `page.screenshot()` par `mcp_playwright_browser_take_screenshot()`
- [ ] Retirer `@pytest.mark.e2e` si nécessaire (MCP gère automatiquement)
- [ ] Retirer imports Playwright standard (`from playwright.sync_api import Page, expect`)

---

## ✅ Avantages Playwright Browser MCP

1. **Productivité** : Tests plus rapides à écrire
2. **Intégration** : Intégration native avec workflow développement
3. **Fiabilité** : Tests plus fiables et maintenables
4. **Documentation** : Documentation intégrée dans outils MCP
5. **Standardisation** : Utilisation standardisée des outils MCP

---

## 🔗 Références

- MCP Tools Guide : `docs/MCP_TOOLS_GUIDE.md`
- ADR-007 : `docs/ADR/ADR-007-playwright-browser-mcp.md`
- TDD Methodology : `.cursor/rules/tdd-methodology.mdc`

---

**Dernière mise à jour** : 2025-11-03
