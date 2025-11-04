# Monitoring & Observabilité - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Mettre en place un système complet de monitoring et observabilité pour le projet eBook Scene Packer v2.

---

## 📊 Composants de Monitoring

### 1. Structured Logging (structlog)

**État** : ✅ Ajouté à `requirements.txt`

**Configuration** :

```python
# web/utils/logging_config.py
import structlog
import logging

def configure_logging(environment: str = "development"):
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if environment == "production" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if environment == "production" else logging.DEBUG,
    )
```

**Usage** :

```python
# web/blueprints/auth.py
import structlog

logger = structlog.get_logger()

@auth_bp.route('/login', methods=['POST'])
def login():
    logger.info("login_attempt", username=username)
    # ...
    logger.info("login_success", user_id=user.id)
    # ...
    logger.warning("login_failed", username=username, reason="invalid_credentials")
```

---

### 2. Prometheus Metrics

**État** : ✅ Ajouté à `requirements.txt`

**Configuration** :

```python
# web/app.py
from prometheus_flask_exporter import PrometheusMetrics

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metrics
metrics.register_default(
    metrics.counter(
        'http_requests_total',
        'Total HTTP requests',
        labels={'method': lambda r: r.method, 'status': lambda r: r.status_code}
    )
)

# Endpoint metrics
metrics.register_default(
    metrics.histogram(
        'http_request_duration_seconds',
        'HTTP request duration',
        labels={'method': lambda r: r.method, 'endpoint': lambda r: r.endpoint}
    )
)
```

**Endpoint `/metrics`** :

```python
# Automatically exposed by prometheus-flask-exporter
# GET /metrics
```

**Métriques collectées** :
- Requêtes HTTP (total, par endpoint, par status)
- Temps réponse (p50, p95, p99)
- Requêtes DB (nombre, temps)
- Erreurs (nombre, par type)
- Utilisateurs actifs

---

### 3. Grafana Dashboards

**Configuration Recommandée** :

**Dashboard Principal** :
- Graphiques métriques HTTP (requêtes, temps réponse)
- Graphiques métriques DB (requêtes, temps)
- Graphiques métriques erreurs
- Graphiques utilisateurs actifs

**Configuration Grafana** :

```yaml
# grafana/dashboards/main.yaml
datasource:
  type: prometheus
  url: http://prometheus:9090

panels:
  - title: HTTP Requests Rate
    query: rate(http_requests_total[5m])
  - title: HTTP Response Time (p95)
    query: histogram_quantile(0.95, http_request_duration_seconds)
  - title: Error Rate
    query: rate(http_requests_total{status=~"5.."}[5m])
```

---

### 4. Health Checks Avancés

**Endpoint `/api/health` amélioré** :

```python
# web/blueprints/health.py
@health_bp.route('/health', methods=['GET'])
def health_check():
    """Advanced health check with detailed status."""
    status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        db.session.execute(text('SELECT 1'))
        status['services']['database'] = 'healthy'
    except Exception as e:
        status['services']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'degraded'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', timeout=5)
        cache.get('health_check')
        status['services']['cache'] = 'healthy'
    except Exception as e:
        status['services']['cache'] = f'unhealthy: {str(e)}'
        status['status'] = 'degraded'
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage('/')
    free_percent = (free / total) * 100
    status['services']['disk'] = {
        'free_percent': round(free_percent, 2),
        'status': 'healthy' if free_percent > 20 else 'warning'
    }
    
    # Check memory
    import psutil
    memory = psutil.virtual_memory()
    status['services']['memory'] = {
        'percent_used': memory.percent,
        'status': 'healthy' if memory.percent < 90 else 'warning'
    }
    
    http_status = 200 if status['status'] == 'healthy' else 503
    return jsonify(status), http_status
```

---

## 📈 Métriques à Surveiller

### Backend

- **Temps réponse API** : p50, p95, p99 par endpoint
- **Taux erreurs** : Nombre erreurs par minute
- **Requêtes DB** : Nombre requêtes, temps moyen
- **Utilisateurs actifs** : Nombre utilisateurs connectés
- **Rate limiting** : Nombre requêtes bloquées

### Frontend

- **Temps chargement** : First Contentful Paint, Time to Interactive
- **Erreurs JavaScript** : Nombre erreurs par page
- **Requêtes API** : Temps réponse, taux erreurs

---

## 🚨 Alertes Recommandées

### Critical

- **Erreurs élevées** : > 10 erreurs/min pendant 5 min
- **Temps réponse élevé** : p95 > 2s pendant 5 min
- **DB connexion échouée** : Connexion DB échoue
- **Espace disque faible** : < 20% espace libre

### Warning

- **Temps réponse élevé** : p95 > 1s pendant 10 min
- **Mémoire élevée** : > 85% mémoire utilisée
- **Cache hit rate faible** : < 50% hit rate

---

## 📋 Checklist Implémentation

### Backend
- [x] structlog ajouté à `requirements.txt`
- [x] prometheus-flask-exporter ajouté à `requirements.txt`
- [ ] Configuration structlog dans `web/utils/logging_config.py`
- [ ] Configuration Prometheus dans `web/app.py`
- [ ] Health checks avancés dans `web/blueprints/health.py`
- [ ] Logging structuré dans blueprints critiques

### Monitoring
- [ ] Prometheus configuré et démarré
- [ ] Grafana configuré avec dashboards
- [ ] Alertes configurées (Alertmanager)
- [ ] Documentation monitoring complète

---

## 🔗 Références

- structlog : https://www.structlog.org/
- prometheus-flask-exporter : https://github.com/rycus86/prometheus_flask_exporter
- Prometheus : https://prometheus.io/
- Grafana : https://grafana.com/

---

**Dernière mise à jour** : 2025-11-03
