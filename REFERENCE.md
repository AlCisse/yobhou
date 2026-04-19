# Documentation de référence Yobhou

## Architecture globale

Le projet Yobhou est divisé en trois parties principales :

1. **Application mobile Flutter** (`/mobile`)
   - Application cross-platform (Android/iOS)
   - Gestion des factures EDG
   - Paiement via Mobile Money
   - Interface agence physique

2. **Backend API Python** (`/backend`)
   - Django + Django REST Framework
   - Gestion des clients, factures, paiements
   - Intégration Mobile Money
   - Gestion des agences

3. **Infrastructure Docker Swarm** (`/infrastructure/docker-swarm`)
   - Orchestration des services
   - Load balancing avec Traefik
   - PostgreSQL pour les données
   - Redis pour le cache
   - Celery pour les tâches asynchrones

## Stack technique

### Mobile
- Flutter (Dart)
- Provider pour la gestion d'état
- Dio pour les appels API
- Retrofit pour la génération de clients API
- GetIt pour l'injection de dépendances

### Backend
- Python 3.10+
- Django 4.2+
- Django REST Framework
- Celery pour les tâches asynchrones
- Redis pour le cache
- PostgreSQL comme base de données

### Infrastructure
- Docker Swarm
- Traefik comme reverse proxy
- Let's Encrypt pour les certificats SSL
- Prometheus + Grafana pour le monitoring

## Services Mobile Money

### Orange Money
- API: `https://api.orangemoney.gn`
- Authentification: OAuth 2.0
- Endpoints:
  - `/v1/payments/init`
  - `/v1/payments/status`
  - `/v1/payments/refund`

### MTN Mobile Money
- API: `https://api.mtn.gn`
- Authentification: OAuth 2.0
- Endpoints:
  - `/v1/payments/create`
  - `/v1/payments/check`
  - `/v1/payments/complete`

## Sécurité

- JWT pour l'authentification
- HTTPS obligatoire
- Validation stricte des entrées
- Sanitization des données
- Logs de sécurité
- Audit des paiements

## Déploiement

### Environnement de développement
```bash
cd backend
docker-compose up -d
cd ../mobile
flutter pub get
flutter run
```

### Environnement de production (Docker Swarm)
```bash
docker stack deploy -c infrastructure/docker-swarm/docker-stack.yml yobhou
```

## Conventions de code

### Backend
- PEP 8 strict
- Type hints obligatoires
- Docstrings Google style
- Services pour toute la logique métier
- Tests unitaires et d'intégration

### Mobile
- Clean Architecture (Domain/Data/Presentation)
- Provider pour l'état
- Dart 3.0+ features
- Tests widget et integration

## Structure des dossiers

### Mobile
```
mobile/
├── lib/
│   ├── main.dart
│   ├── services/       # API calls
│   ├── models/         # Data models
│   ├── pages/          # Screen pages
│   ├── widgets/        # Reusable widgets
│   ├── utils/          # Helper functions
│   └── providers/      # State management
├── android/
├── ios/
└── pubspec.yaml
```

### Backend
```
backend/
├── config/             # Project settings
├── apps/               # Django apps
│   ├── billing/
│   ├── payments/
│   ├── customers/
│   └── agencies/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── docker-compose.yml
```

### Infrastructure
```
infrastructure/docker-swarm/
├── docker-stack.yml    # Main stack definition
├── traefik/            # Reverse proxy config
├── postgres/           # Database setup
├── redis/              # Cache setup
├── celery/             # Task queues
└── monitoring/         # Metrics & dashboards
```