# Configurations pour Yobhou

Ce dossier contient les configurations spécifiques pour le projet Yobhou.

## Fichiers de configuration

### Docker Compose (backend)
- `docker-compose.yml` : Configuration principale
- `docker-compose.dev.yml` : Configuration développement
- `docker-compose.prod.yml` : Configuration production

### Docker Swarm
- `docker-stack.yml` : Stack de production

### Traefik
- `traefik.yml` : Configuration principale
- `traefik.dev.yml` : Configuration développement

## Variables d'environnement

### Backend (Docker Secrets OBLIGATOIRE)
```
DJANGO_SECRET_KEY=/run/secrets/django_secret_key
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@db:5432/yobhou
REDIS_URL=redis://redis:6379/0
ORANGE_MONEY_API_KEY=/run/secrets/orange_money_api_key
MTN_MOBILE_MONEY_API_KEY=/run/secrets/mtn_mobile_money_api_key
ORANGE_MONEY_SHARED_SECRET=/run/secrets/orange_money_shared_secret
MTN_MOBILE_MONEY_SHARED_SECRET=/run/secrets/mtn_mobile_money_shared_secret
QR_CODE_ENCRYPTION_KEY=/run/secrets/qr_code_encryption_key
```

### Mobile
```
API_BASE_URL=https://api.yobhou.gn
ORANGE_MERCHANT_ID=/run/secrets/orange_merchant_id
MTN_MERCHANT_ID=/run/secrets/mtn_merchant_id
QR_CODE_DECRYPTION_KEY=/run/secrets/qr_code_encryption_key
```

## Fichiers de configuration pour les services

### PostgreSQL
- `init-scripts/` : Scripts d'initialisation
- `volumes/` : Volumes persistants

### Redis
- `volumes/` : Volumes persistants

### Celery
- `worker.sh` : Script pour les workers
- `beat.sh` : Script pour le scheduler

## Monitoring
- `prometheus.yml` : Configuration Prometheus
- `grafana-dashboard.yml` : Dashboard Grafana