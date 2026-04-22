# 🐳 SWARM DEPLOYMENT GUIDE - Yobhou Fintech

**Date** : 2026-04-22  
**Version** : 1.0  
**Environnement** : Production (Docker Swarm)

---

## 📋 Prérequis

### Infrastructure
- **Docker Swarm** : 1 manager + 2 workers minimum
- **RAM** : 16GB minimum (32GB recommandé)
- **CPU** : 8 cores minimum
- **Stockage** : 100GB SSD minimum
- **Réseau** : Ports 80, 443, 22 ouverts

### Comptes & Services
- [ ] Docker Hub account
- [ ] GitHub account (CI/CD)
- [ ] DigitalOcean account (ou équivalent)
- [ ] S3-compatible storage (DO Spaces)
- [ ] Nom de domaine (yobhou.gn recommandé)
- [ ] Certificat SSL (Let's Encrypt auto)

---

## 🔐 Étape 1 : Configuration des Secrets

### Création des Secrets Docker

```bash
# Connecter au manager Swarm
ssh root@swarm-manager

# 1. Django Secret Key (générer une fois)
openssl rand -base64 48 | docker secret create django_secret_key -

# 2. Database Password
openssl rand -base64 32 | docker secret create db_password -

# 3. Encryption Key (AES-256)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" | docker secret create encryption_key -

# 4. ELK Password (Kibana/Elasticsearch)
openssl rand -base64 32 | docker secret create elk_password -

# 5. Grafana Password
openssl rand -base64 32 | docker secret create grafana_password -

# 6. AWS/S3 Credentials (archive 10 ans)
echo "VOTRE_AWS_ACCESS_KEY" | docker secret create aws_access_key -
echo "VOTRE_AWS_SECRET_KEY" | docker secret create aws_secret_key -
```

### Vérification des Secrets

```bash
docker secret ls
# Doit afficher :
# django_secret_key, db_password, encryption_key, elk_password, grafana_password, aws_access_key, aws_secret_key
```

---

## 📦 Étape 2 : Déploiement du Stack

### Clonage du Dépôt

```bash
cd /opt/yobhou
git clone https://github.com/AlCisse/yobhou.git
cd yobhou/backend
```

### Configuration d'Environnement

```bash
cat > .env << EOF
# PostgreSQL
POSTGRES_USER=yobhou_user
POSTGRES_PASSWORD=yobhou_password
POSTGRES_DB=yobhou_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Elasticsearch
ELASTIC_PASSWORD=elk_password_from_secret

# Grafana
GRAFANA_PASSWORD=grafana_password_from_secret

# S3/Glacier (archive 10 ans)
ARCHIVE_S3_BUCKET=yobhou-audit-logs
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=aws_access_key_from_secret
AWS_SECRET_ACCESS_KEY=aws_secret_key_from_secret

# Fernet Key (chiffrement logs)
ENCRYPTION_KEY=encryption_key_from_secret
EOF
```

### Déploiement du Stack

```bash
# Déployer le stack backend
docker stack deploy -c docker-stack.yml yobhou-backend

# Vérifier le déploiement
docker stack ls
docker stack ps yobhou-backend
```

### Vérification des Services

```bash
# Liste des services
docker service ls | grep yobhou

# Logs web
docker service logs yobhou-backend_web --tail 50

# Logs OCR
docker service logs yobhou-backend_ocr_worker --tail 50
```

---

## 🌐 Étape 3 : Configuration Traefik (HTTPS)

### Labels Traefik dans docker-stack.yml

```yaml
services:
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.yobhou.rule=Host(`api.yobhou.gn`)"
      - "traefik.http.routers.yobhou.entrypoints=websecure"
      - "traefik.http.routers.yobhou.tls=true"
      - "traefik.http.routers.yobhou.tls.certresolver=letsencrypt"
      - "traefik.http.services.yobhou.loadbalancer.server.port=8000"
```

### Let's Encrypt Configuration

```bash
# Dans docker-stack.yml, Traefik doit inclure :
command:
  - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
  - "--certificatesresolvers.letsencrypt.acme.email=tech@yobhou.gn"
  - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
```

### Redémarrage Traefik

```bash
docker service update --force yobhou-backend_traefik
```

---

## 🧪 Étape 4 : Tests de Validation

### 4.1 Vérifier l'API

```bash
curl -X GET https://api.yobhou.gn/api/health
# Doit retourner : {"status": "ok"}
```

### 4.2 Vérifier l'Admin Django

```
URL : https://api.yobhou.gn/admin/
# Login : admin (via createsuperuser dans le container)
```

### 4.3 Vérifier Kibana (Logs)

```
URL : https://api.yobhou.gn/kibana/
Login : elastic / [elk_password_from_secret]
```

### 4.4 Vérifier Grafana (Métriques)

```
URL : https://api.yobhou.gn/grafana/
Login : admin / [grafana_password_from_secret]
```

---

## 📊 Étape 5 : Configuration des Alertes

### Alertmanager (Prometheus)

Créer `prometheus/alertmanager.yml` :

```yaml
global:
  smtp_smarthost: 'smtp.sendgrid.net:587'
  smtp_from: 'alerts@yobhou.gn'
  smtp_auth_username: 'apikey'
  smtp_auth_password: 'VOTRE_SENDGRID_KEY'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email-notifications'

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'tech@yobhou.gn'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

### Alertes Critiques

| Alerte | Seuil | Canal | Délai |
|--------|-------|-------|-------|
| DB Down | 1 min | SMS + Email | Immédiat |
| Transaction > 1M GNF | Unique | Email + Dashboard | < 5 min |
| Erreur Auth > 5/min | 5/min | Dashboard | < 1 min |
| Backup Échoué | 1 échec | Email | < 1h |
| Espace Disque > 90% | 90% | Email | < 1h |

---

## 🔄 Étape 6 : CI/CD (GitHub Actions)

### Workflow de Déploiement

Créer `.github/workflows/deploy.yml` :

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t alcisse/yobhou-backend:latest backend/
      - name: Push to Docker Hub
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push alcisse/yobhou-backend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Swarm
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SWARM_MANAGER_HOST }}
          username: ${{ secrets.SWARM_MANAGER_USER }}
          key: ${{ secrets.SWARM_MANAGER_KEY }}
          script: |
            cd /opt/yobhou
            git pull
            docker stack deploy -c docker-stack.yml yobhou-backend
```

### Secrets GitHub

Aller sur : `https://github.com/AlCisse/yobhou/settings/secrets/actions`

Ajouter :
- `DOCKER_USERNAME` : Votre username Docker Hub
- `DOCKER_PASSWORD` : Votre password/token Docker Hub
- `SWARM_MANAGER_HOST` : IP du manager Swarm
- `SWARM_MANAGER_USER` : User SSH du manager
- `SWARM_MANAGER_KEY` : Clé privée SSH

---

## ✅ Checklist de Production

### Sécurité
- [ ] Tous les secrets dans Docker Secrets (rien dans le code)
- [ ] TLS 1.3 activé (SSL Labs test : A+)
- [ ] Rate limiting activé (100 req/min)
- [ ] HSTS activé avec preload
- [ ] Headers de sécurité (CSP, X-Frame-Options, etc.)

### Audit & Conformité
- [ ] Logs immuables configurés (ELK + S3 Glacier)
- [ ] Rétention 10 ans activée
- [ ] AML checker fonctionnel
- [ ] Plafonds configurés (1M/jour, 5M/mois)
- [ ] Dashboard admin avec alertes AML

### Monitoring
- [ ] Prometheus scrape fonctionnel
- [ ] Grafana dashboards configurés
- [ ] Alertes critiques testées
- [ ] On-call astreinte configurée

### Backup & PRA
- [ ] Backup DB automatique (1h)
- [ ] Archive S3 Glacier fonctionnelle
- [ ] Test de restauration réussi
- [ ] RTO < 4h validé
- [ ] RPO < 1h validé

### Performance
- [ ] Tests de charge (10k users simultanés)
- [ ] Temps de réponse API < 200ms
- [ ] OCR < 5s par image
- [ ] Cache Redis fonctionnel

---

## 🎯 Go-Live

### J-7 : Freeze Code
- [ ] Aucun nouveau feature
- [ ] Tests de régression complets
- [ ] Pentest externe validé

### J-3 : Déploiement Staging
- [ ] Déployer sur environnement staging
- [ ] Tests e2e avec données réelles
- [ ] Validation équipe

### J-1 : Backup Final
- [ ] Backup complet production
- [ ] Snapshot DB
- [ ] Vérification intégrité

### J-0 : Go-Live
- [ ] Déploiement production (matin 6h UTC)
- [ ] Surveillance renforcée (toutes les 15 min)
- [ ] Communication équipe (Slack/WhatsApp)
- [ ] Support client prêt

### J+1 : Post-Mortem
- [ ] Revue des incidents (si any)
- [ ] Métriques de performance
- [ ] Feedback utilisateurs
- [ ] Ajustements si nécessaire

---

## 📞 Support & Maintenance

### Contacts Urgents
- **CTO** : [votre_contact]
- **Lead Dev** : [contact_dev]
- **Ops** : [contact_ops]

### Runbooks
- [ ] Incident DB : `docs/runbook-db-down.md`
- [ ] Incident Sécurité : `docs/runbook-security.md`
- [ ] Incident Performance : `docs/runbook-performance.md`

### Maintenance Régulière
- **Quotidien** : Vérifier dashboard Grafana, logs critiques
- **Hebdo** : Review alertes AML, backups
- **Mensuel** : Rotation des secrets, update dépendances
- **Trimestriel** : Audit sécurité, tests de charge
- **Annuel** : Pentest externe, certification

---

**Last Updated** : 2026-04-22  
**Version** : 1.0  
**Status** : ✅ Guide de déploiement complet  
**Branch** : `main` (commit 8b9c83f)