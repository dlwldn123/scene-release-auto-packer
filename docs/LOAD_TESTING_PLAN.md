# Plan Montée en Charge - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Définir le plan de montée en charge pour garantir que l'application peut supporter la charge prévue en production.

---

## 📊 Objectifs Performance

### Objectifs Actuels

- **Temps réponse API** : < 200ms (p95)
- **Taux erreurs** : < 0.1%
- **Support utilisateurs** : 100 utilisateurs simultanés
- **Support données** : 1000+ releases

### Objectifs Production

- **Temps réponse API** : < 200ms (p95), < 500ms (p99)
- **Taux erreurs** : < 0.1%
- **Support utilisateurs** : 500 utilisateurs simultanés
- **Support données** : 10 000+ releases
- **Disponibilité** : 99.9% (uptime)

---

## 🧪 Tests de Charge

### Outils

**Recommandé** : **Locust** (Python) ou **k6** (JavaScript)

**Installation Locust** :

```bash
pip install locust
```

**Installation k6** :

```bash
# Sur Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

---

## 📋 Scénarios de Charge

### Scénario 1 : Charge Normale

**Objectif** : Valider fonctionnement sous charge normale

**Paramètres** :
- **Utilisateurs** : 50 utilisateurs simultanés
- **Durée** : 30 minutes
- **Ramp-up** : 10 utilisateurs/seconde

**Scénario** :
1. Login (50%)
2. Dashboard (30%)
3. Liste Releases (40%)
4. Création Release (10%)
5. Gestion Rules (20%)

**Métriques à Mesurer** :
- Temps réponse par endpoint (p50, p95, p99)
- Taux erreurs
- Utilisation CPU/Mémoire
- Requêtes DB/seconde
- Taux cache hit

**Critères de Réussite** :
- ✅ Temps réponse < 200ms (p95)
- ✅ Taux erreurs < 0.1%
- ✅ CPU < 80%
- ✅ Mémoire < 80%

---

### Scénario 2 : Charge Élevée

**Objectif** : Valider fonctionnement sous charge élevée

**Paramètres** :
- **Utilisateurs** : 200 utilisateurs simultanés
- **Durée** : 1 heure
- **Ramp-up** : 20 utilisateurs/seconde

**Scénario** : Identique Scénario 1

**Métriques à Mesurer** : Identique Scénario 1

**Critères de Réussite** :
- ✅ Temps réponse < 500ms (p95)
- ✅ Taux erreurs < 1%
- ✅ CPU < 90%
- ✅ Mémoire < 90%

---

### Scénario 3 : Charge Maximale

**Objectif** : Identifier limites système

**Paramètres** :
- **Utilisateurs** : 500 utilisateurs simultanés
- **Durée** : 2 heures
- **Ramp-up** : 50 utilisateurs/seconde

**Scénario** : Identique Scénario 1

**Métriques à Mesurer** : Identique Scénario 1 + Points de rupture

**Critères de Réussite** :
- Identifier point de rupture
- Identifier bottlenecks
- Plan optimisations

---

### Scénario 4 : Spike Test

**Objectif** : Valider résilience face à pics de charge

**Paramètres** :
- **Utilisateurs** : 0 → 300 → 0 (spike)
- **Durée** : 15 minutes
- **Spike** : 100 utilisateurs en 10 secondes

**Scénario** : Identique Scénario 1

**Métriques à Mesurer** : Identique Scénario 1 + Récupération

**Critères de Réussite** :
- ✅ Système récupère après spike
- ✅ Pas de crash
- ✅ Temps réponse se stabilise

---

## 📝 Scripts Tests de Charge

### Locust (Python)

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class ApplicationUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting."""
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(5)
    def view_dashboard(self):
        """View dashboard."""
        self.client.get("/api/dashboard/stats", headers=self.headers)
    
    @task(4)
    def list_releases(self):
        """List releases."""
        self.client.get("/api/releases", headers=self.headers)
    
    @task(2)
    def list_rules(self):
        """List rules."""
        self.client.get("/api/rules", headers=self.headers)
    
    @task(1)
    def create_release(self):
        """Create release."""
        self.client.post("/api/wizard/create", json={
            "group": "TestGroup",
            "release_type": "EBOOK"
        }, headers=self.headers)
```

**Exécution** :

```bash
# Mode web UI
locust -f tests/load/locustfile.py --host=http://localhost:5000

# Mode headless
locust -f tests/load/locustfile.py --host=http://localhost:5000 --headless -u 50 -r 10 -t 30m
```

---

### k6 (JavaScript)

```javascript
// tests/load/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up
    { duration: '30m', target: 50 }, // Maintain
    { duration: '30s', target: 0 },  // Ramp-down
  ],
};

let token = '';

export function setup() {
  // Login
  const loginRes = http.post('http://localhost:5000/api/auth/login', JSON.stringify({
    username: 'testuser',
    password: 'password'
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  token = JSON.parse(loginRes.body).access_token;
  return { token };
}

export default function(data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };
  
  // Dashboard
  const dashboardRes = http.get('http://localhost:5000/api/dashboard/stats', { headers });
  check(dashboardRes, {
    'dashboard status 200': (r) => r.status === 200,
    'dashboard response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
  
  // List releases
  const releasesRes = http.get('http://localhost:5000/api/releases', { headers });
  check(releasesRes, {
    'releases status 200': (r) => r.status === 200,
    'releases response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
}
```

**Exécution** :

```bash
k6 run tests/load/load_test.js
```

---

## 🚀 Stratégie Scaling

### Horizontal Scaling

**Configuration** :
- **Load Balancer** : Nginx (round-robin)
- **Instances Flask** : 3-5 instances
- **Session Sharing** : Redis (si nécessaire)

**Architecture** :

```
Internet
  ↓
Nginx (Load Balancer)
  ↓
┌─────────┬─────────┬─────────┐
│ Flask 1 │ Flask 2 │ Flask 3 │
└─────────┴─────────┴─────────┘
  ↓
MySQL (Primary + Replica)
```

**Configuration Nginx** :

```nginx
# nginx/nginx.conf
upstream flask_app {
    least_conn;
    server flask1:5000;
    server flask2:5000;
    server flask3:5000;
}

server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### Vertical Scaling

**Optimisations** :

- **Optimisation Requêtes DB** :
  - Indexes optimisés
  - Requêtes optimisées (eager loading)
  - Connection pooling

- **Caching Stratégique** :
  - Redis pour cache distribué
  - Cache endpoints fréquents
  - Cache invalidation stratégique

- **Optimisation Code** :
  - Code optimisé (éviter N+1 queries)
  - Lazy loading frontend
  - Code splitting

---

## 📊 Métriques Production

### Métriques à Surveiller

**Backend** :
- Temps réponse API (p50, p95, p99)
- Taux erreurs (4xx, 5xx)
- Requêtes DB/seconde
- Taux cache hit
- Utilisation CPU/Mémoire

**Frontend** :
- Temps chargement (First Contentful Paint)
- Temps navigation (Time to Interactive)
- Erreurs JavaScript
- Taille bundle

**Infrastructure** :
- Utilisation CPU/Mémoire serveurs
- Utilisation espace disque
- Bandwidth réseau
- Connexions DB

---

## 🚨 Plan Alertes Production

### Critical

- **Erreurs élevées** : > 10 erreurs/min pendant 5 min
- **Temps réponse élevé** : p95 > 2s pendant 5 min
- **DB connexion échouée** : Connexion DB échoue
- **Espace disque faible** : < 20% espace libre
- **CPU élevé** : > 90% CPU pendant 10 min

### Warning

- **Temps réponse élevé** : p95 > 1s pendant 10 min
- **Mémoire élevée** : > 85% mémoire utilisée
- **Cache hit rate faible** : < 50% hit rate
- **Requêtes DB élevées** : > 1000 req/s

---

## 📋 Checklist Montée en Charge

### Tests
- [ ] Tests charge normaux (50 utilisateurs)
- [ ] Tests charge élevée (200 utilisateurs)
- [ ] Tests charge maximale (500 utilisateurs)
- [ ] Tests spike (300 utilisateurs spike)
- [ ] Analyse résultats
- [ ] Identification bottlenecks

### Scaling
- [ ] Configuration load balancer (Nginx)
- [ ] Configuration multi-instances Flask
- [ ] Configuration Redis cache distribué
- [ ] Configuration MySQL replica

### Monitoring
- [ ] Métriques production configurées
- [ ] Alertes configurées
- [ ] Dashboards Grafana créés
- [ ] On-call rotation configurée

---

## 🔗 Références

- Locust : https://locust.io/
- k6 : https://k6.io/
- Performance : `docs/PERFORMANCE.md`
- Monitoring : `docs/MONITORING.md`

---

**Dernière mise à jour** : 2025-11-03
