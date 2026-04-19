# Yobhou Backend

Backend Django pour le projet Yobhou - Paiement factures électricité en Guinée.

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- PostgreSQL
- Redis

### Configuration locale

1. Cloner le dépôt
2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Créer les migrations et les appliquer :
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Lancer le serveur de développement :
```bash
python manage.py runserver
```

### Configuration avec Docker

1. Construire et lancer les conteneurs :
```bash
docker-compose up --build
```

2. Accéder à l'API à l'adresse `http://localhost:8000/api/`

## 🧠 OCR avec PaddleOCR

Le service OCR utilise PaddleOCR pour extraire les données des factures EDG et des photos de compteurs.

### Fonctionnalités

- Extraction automatique du numéro de compteur
- Extraction de l'index (consommation kWh)
- Validation de confiance OCR
- Support d'images JPG, JPEG, PNG, PDF

## 🔐 Sécurité

- Tous les secrets sont gérés via Docker Secrets
- Containers en lecture seule (`read_only: true`) pour les services sensibles
- Segmentation réseau stricte
- Aucun secret en clair dans le code

## 📦 Structure du projet

```
backend/
├── apps/              # Applications Django
│   ├── users/         # Gestion des utilisateurs
│   ├── meters/        # Relevés de compteurs
│   └── transactions/  # Transactions de paiement
├── ocr_service/       # Service OCR PaddleOCR
├── api/               # API REST
├── core/              # Configuration Django
├── Dockerfile         # Configuration Docker
└── requirements.txt   # Dépendances Python
```

## 🛠️ Développement

### Tests

```bash
pytest
```

### Formatage

```bash
black .
```

### Linting

```bash
pylint backend/
```

## 📝 Endpoints API

- `POST /api/upload-invoice/` - Upload et traitement d'une facture
- `POST /api/capture-meter/` - Capture et OCR d'un photo de compteur
- `POST /api/validate-reading/` - Validation des données OCR

## 🔄 CI/CD

GitHub Actions pour :
- Linting et tests automatiques
- Build et déploiement Docker
- Gestion des secrets via GitHub Secrets