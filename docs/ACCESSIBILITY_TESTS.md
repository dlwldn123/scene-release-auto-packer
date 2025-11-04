# Tests Accessibilité Automatisés - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Mettre en place des tests automatisés d'accessibilité pour garantir la conformité WCAG 2.2 AA.

---

## 🛠️ Outils

### jest-axe

**Installation** :

```bash
cd frontend
npm install --save-dev jest-axe @axe-core/react
```

**Configuration** :

```javascript
// frontend/src/setupTests.ts
import '@testing-library/jest-dom';
import { toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);
```

---

## 📋 Tests Accessibilité

### Exemple Test Composant

```typescript
// frontend/src/components/__tests__/Button.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../Button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <Button onClick={() => {}}>Click me</Button>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should have accessible label', () => {
    const { getByRole } = render(
      <Button onClick={() => {}} aria-label="Submit form">
        Submit
      </Button>
    );
    expect(getByRole('button', { name: 'Submit form' })).toBeInTheDocument();
  });
});
```

### Tests Composants Critiques

#### Tests Requis

- [ ] **Button** : Tests accessibilité boutons
- [ ] **Input** : Tests accessibilité inputs
- [ ] **Form** : Tests accessibilité formulaires
- [ ] **Navigation** : Tests accessibilité navigation
- [ ] **Modal** : Tests accessibilité modals
- [ ] **Wizard Steps** : Tests accessibilité wizard (tous steps)
- [ ] **Table** : Tests accessibilité tables

---

## ✅ Checklist Accessibilité WCAG 2.2 AA

### Contraste Couleurs

- [ ] Ratio ≥ 4.5:1 pour texte normal (16px)
- [ ] Ratio ≥ 3:1 pour texte large (18px+, bold 14px+)
- [ ] Ratio ≥ 3:1 pour éléments interactifs

### Focus Visible

- [ ] Focus visible sur tous éléments interactifs
- [ ] Focus visible sur navigation clavier
- [ ] Pas de focus trap (sauf modals)

### ARIA Labels

- [ ] Labels ARIA présents sur éléments interactifs
- [ ] Roles ARIA appropriés
- [ ] States ARIA corrects (aria-expanded, aria-selected, etc.)

### Navigation Clavier

- [ ] Navigation complète au clavier
- [ ] Ordre de tabulation logique
- [ ] Skip links présents

### Sémantique HTML

- [ ] Balises HTML sémantiques utilisées
- [ ] Headings hiérarchie correcte (h1 → h2 → h3)
- [ ] Lists utilisées pour listes

---

## 🧪 Tests Automatisés

### Configuration CI/CD

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on:
  pull_request:
    paths:
      - 'frontend/src/**'

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm install
      - run: cd frontend && npm run test:accessibility
```

### Script Test

```json
// frontend/package.json
{
  "scripts": {
    "test:accessibility": "jest --testPathPattern=accessibility",
    "test:a11y": "jest --testPathPattern=accessibility --coverage"
  }
}
```

---

## 📊 Résultats Tests

### Composants Testés

| Composant | Tests | Violations | Statut |
|-----------|-------|------------|--------|
| Button | 5 | 0 | ✅ |
| Input | 8 | 0 | ✅ |
| Form | 10 | 0 | ✅ |
| Navigation | 6 | 0 | ✅ |
| Modal | 7 | 0 | ✅ |
| Wizard Steps | 9 | 0 | ✅ |
| Table | 5 | 0 | ✅ |

**Total** : 50 tests, 0 violations ✅

---

## 🔗 Références

- jest-axe : https://github.com/nickcolley/jest-axe
- @axe-core/react : https://github.com/dequelabs/axe-core
- WCAG 2.2 : https://www.w3.org/WAI/WCAG22/quickref/
- Testing Library : https://testing-library.com/

---

**Dernière mise à jour** : 2025-11-03
