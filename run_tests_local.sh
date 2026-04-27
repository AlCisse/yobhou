#!/bin/bash
# Script de test local sans Docker
# À exécuter dans l'environnement virtuel Python

set -e

echo "🧪 Yobhou Test Runner"
echo "======================"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Vérifier Python
echo -e "${YELLOW}Vérification Python...${NC}"
python3 --version || { echo -e "${RED}Python3 non trouvé${NC}"; exit 1; }

# Vérifier virtualenv
echo -e "${YELLOW}Activation virtualenv...${NC}"
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
elif [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo -e "${YELLOW}Création virtualenv...${NC}"
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

cd backend

# Tests unitaires
echo -e "\n${YELLOW}Tests Utilisateurs...${NC}"
python manage.py test apps.users.tests -v 2

echo -e "\n${YELLOW}Tests Compteurs...${NC}"
python manage.py test apps.meters.tests -v 2

echo -e "\n${YELLOW}Tests Transactions...${NC}"
python manage.py test apps.transactions.tests -v 2

echo -e "\n${YELLOW}Tests OCR...${NC}"
python manage.py test ocr_service.tests -v 2

echo -e "\n${YELLOW}Tests Paiements...${NC}"
python manage.py test apps.payments.tests -v 2

# Tests intégration
echo -e "\n${YELLOW}Tests Intégration...${NC}"
python manage.py test apps.payments.tests_integration -v 2

# Rapport couverture
echo -e "\n${YELLOW}Rapport Couverture...${NC}"
pytest --cov=. --cov-report=html --cov-report=term

echo -e "\n${GREEN}✅ Tests terminés avec succès${NC}"
echo -e "Rapport HTML : backend/htmlcov/index.html"
