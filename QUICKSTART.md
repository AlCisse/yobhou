# 🚀 Yobhou Fintech - Quick Start Guide

## ⚡ Démarrage Rapide (5 minutes)

Ce guide vous permet de lancer le backend et d'exécuter tous les tests.

---

## 📋 Prérequis

- **Python** : 3.11+
- **pip** : 21.0+
- **PostgreSQL** : 15+ (ou Docker)
- **Redis** : 7+ (ou Docker)

---

## 🔧 Option 1 : Docker (Recommandé)

### 1. Lancer avec Docker Compose (Dev)

```bash
cd backend

# Construire et lancer tous les services
docker-compose -f docker-compose.dev.yml up --build

# Le backend sera accessible sur http://localhost:8000
```

### 2. Tester les Endpoints

```bash
# Health check
curl http://localhost:8000/api/health/

# Inscription
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "phone_number": "+224601234567",
    "password": "Test1234",
    "password_confirm": "Test1234",
    "date_of_birth": "1990-01-01"
  }'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Test1234"}'
```

### 3. Exécuter les Tests

```bash
# Dans un nouveau terminal
docker-compose -f docker-compose.dev.yml exec web pytest -v --cov
```

---

## 🔧 Option 2 : Local (Sans Docker)

### 1. Installer Dépendances

```bash
cd backend

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurer Base de Données

```bash
# Copier .env
cp .env.example .env

# Éditer .env avec vos credentials PostgreSQL
# POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

# Ou utiliser SQLite pour test rapide
# Dans core/settings.py, remplacer DATABASES par :
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

### 3. Générer Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer Superuser

```bash
python manage.py createsuperuser
# Email : admin@yobhou.gn
# Password : (choisir un mot de passe fort)
```

### 5. Lancer Serveur

```bash
# Development
python manage.py runserver

# Production (Gunicorn)
gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 2 core.wsgi:application
```

### 6. Exécuter Tests

```bash
# Tous les tests
pytest -v --cov

# Tests spécifiques
pytest apps/users/tests.py -v
pytest apps/users/tests_integration.py -v
pytest apps/meters/tests.py -v
pytest apps/transactions/tests.py -v
pytest ocr_service/tests.py -v

# Avec couverture de code
pytest --cov=. --cov-report=html
# Ouvrir : htmlcov/index.html
```

---

## 🧪 Tests Disponibles

| Fichier | Tests | Description |
|---------|-------|-------------|
| `apps/users/tests.py` | 10+ | User model, auth endpoints |
| `apps/users/tests_integration.py` | 20+ | API integration (login, register, profile) |
| `apps/meters/tests.py` | 10+ | MeterReading model, OCR data |
| `apps/transactions/tests.py` | 15+ | Transaction model, AML checker |
| `ocr_service/tests.py` | 15+ | PaddleOCR wrapper |

**Total : 60+ tests automatisés**

---

## 📊 Endpoints API à Tester

### 🔐 Authentification

```bash
# Health check (no auth)
GET /api/health/

# Inscription
POST /api/register/
{
  "username": "testuser",
  "phone_number": "+224601234567",
  "password": "Test1234",
  "password_confirm": "Test1234",
  "date_of_birth": "1990-01-01"
}

# Connexion
POST /api/login/
{
  "username": "testuser",
  "password": "Test1234"
}
# Retourne : access_token, refresh_token, user_data

# Rafraîchir token
POST /api/token/refresh/
{
  "refresh": "your_refresh_token"
}

# Profil (auth requis)
GET /api/profile/
Authorization: Bearer your_access_token

# Logout
POST /api/logout/
Authorization: Bearer your_access_token
```

### 📸 OCR & Meter Reading

```bash
# Upload facture (auth requis)
POST /api/upload-invoice/
Authorization: Bearer your_access_token
Content-Type: multipart/form-data
invoice: [file image.jpg]

# Capture compteur (auth requis)
POST /api/capture-meter/
Authorization: Bearer your_access_token
Content-Type: multipart/form-data
meter_photo: [file image.jpg]

# Valider relevé (auth requis)
POST /api/validate-reading/
Authorization: Bearer your_access_token
Content-Type: application/json
{
  "meter_number": "12345678",
  "current_index": 450.5,
  "previous_index": 400.0,
  "meter_number_confidence": 0.95,
  "index_confidence": 0.92
}
```

---

## 🐛 Dépannage

### Erreur : ModuleNotFoundError

```bash
# Réinstaller requirements
pip install -r requirements.txt
```

### Erreur : Database connection failed

```bash
# Vérifier PostgreSQL tourne
sudo systemctl status postgresql

# Ou utiliser Docker
docker run -d --name postgres \
  -e POSTGRES_USER=yobhou_user \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=yobhou_db \
  -p 5432:5432 \
  postgres:15
```

### Erreur : Migrations pending

```bash
python manage.py makemigrations
python manage.py migrate
```

### Erreur : Port 8000 already in use

```bash
# Changer port
python manage.py runserver 0.0.0.0:8001
```

---

## ✅ Checklist de Validation

- [ ] Backend lancé sans erreur
- [ ] Health check retourne `{"status": "ok"}`
- [ ] Inscription fonctionne
- [ ] Login retourne tokens JWT
- [ ] Profil accessible avec token
- [ ] Tests passent (60+ tests)
- [ ] Couverture tests > 80%

---

## 📈 Prochaines Étapes

1. ✅ Backend local fonctionnel
2. ⏭️ Flutter mobile app
3. ⏭️ Déploiement Docker Swarm
4. ⏭️ Tests utilisateurs pilotes

---

**🎉 Une fois cette checklist validée, votre backend Yobhou est opérationnel !**

**Support** : Consultez `DEPLOYMENT.md` et `SECURITY_ARCHITECTURE.md` pour plus de détails.
