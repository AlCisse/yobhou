# 🧪 Script de Test - Scénario d'Inscription Yobhou

Ce script permet de tester le flux complet d'inscription avec OCR EDG.

## 📋 Prérequis

1. **Installer les dépendances** (sur le VPS ou environnement Docker) :
```bash
cd /home/node/.openclaw/workspace/yobhou/backend
pip install -r requirements.txt
```

2. **Appliquer les migrations** :
```bash
python manage.py migrate
```

3. **Lancer le serveur** :
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🔧 Script de Test Automatisé

```bash
#!/bin/bash
# test_inscription.sh - Test du flux d'inscription Yobhou

BASE_URL="http://localhost:8000"

echo "🛡️  Yobhou Fintech - Test du Scénario d'Inscription"
echo "=================================================="

# Screen 1 : Inscription
echo ""
echo "📝 Screen 1 : Inscription..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+224620123456",
    "date_of_birth": "1995-05-15",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }')

echo "Réponse : $REGISTER_RESPONSE"

# Extraire user_id si succès
USER_ID=$(echo $REGISTER_RESPONSE | grep -o '"user_id": [0-9]*' | grep -o '[0-9]*')

if [ -z "$USER_ID" ]; then
    echo "❌ Échec de l'inscription"
    exit 1
fi

echo "✅ Inscription réussie (user_id: $USER_ID)"

# Screen 2 : Login JWT
echo ""
echo "🔑 Screen 2 : Login JWT..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_224620123456",
    "password": "SecurePass123"
  }')

echo "Réponse : $LOGIN_RESPONSE"

# Extraire le token d'accès
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access": "[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Échec du login"
    exit 1
fi

echo "✅ Login réussi (token extrait)"

# Screen 3 : Upload Facture EDG
echo ""
echo "📄 Screen 3 : Upload Facture EDG..."
echo "⚠️  Remplacez /path/to/edg_invoice.jpg par votre image de facture"

# Créer une image test factice (optionnel)
# convert -size 800x600 xc:white -fill black -draw "text 100,100 'EDG Facture'" test_invoice.jpg

if [ -f "test_invoice.jpg" ]; then
    INVOICE_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/upload-invoice/" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -F "invoice=@test_invoice.jpg")
    
    echo "Réponse : $INVOICE_RESPONSE"
    
    # Vérifier si KYC est vérifié
    if echo $INVOICE_RESPONSE | grep -q '"kyc_status": "verified"'; then
        echo "✅ KYC vérifié avec succès"
    else
        echo "⚠️  KYC en attente de validation"
    fi
else
    echo "⚠️  Aucun fichier test_invoice.jpg trouvé"
    echo "   Pour tester, placez une image de facture EDG dans le dossier courant"
fi

# Vérifier le profil utilisateur
echo ""
echo "👤 Vérification du profil utilisateur..."
PROFILE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/profile/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "Profil : $PROFILE_RESPONSE"

echo ""
echo "=================================================="
echo "✅ Test terminé"
```

---

## 🧪 Tests Unitaires des Champs EDG

```python
# test_edg_ocr.py
import unittest
from ocr_service.paddle_ocr_wrapper import PaddleOCRService

class TestEDGInvoiceExtraction(unittest.TestCase):
    
    def setUp(self):
        self.ocr = PaddleOCRService()
    
    def test_extract_meter_number(self):
        """Test l'extraction du numéro de compteur"""
        text_lines = ["Compteur N°: 12345678", "EDG Facture"]
        result = self.ocr.extract_edg_invoice_data(text_lines)
        self.assertEqual(result['numero_compteur'], '12345678')
    
    def test_extract_nom(self):
        """Test l'extraction du nom"""
        text_lines = ["Nom: Jean Dupont", "Kaloum"]
        result = self.ocr.extract_edg_invoice_data(text_lines)
        self.assertEqual(result['nom'], 'Jean Dupont')
    
    def test_extract_quartier(self):
        """Test l'extraction du quartier"""
        text_lines = ["Quartier: Kaloum", "Conakry"]
        result = self.ocr.extract_edg_invoice_data(text_lines)
        self.assertEqual(result['quartier'], 'Kaloum')
    
    def test_extract_tranche(self):
        """Test l'extraction de la tranche"""
        text_lines = ["Tranche 2", "Consommation: 500 kWh"]
        result = self.ocr.extract_edg_invoice_data(text_lines)
        self.assertEqual(result['tranche'], 'Tranche 2')
    
    def test_extract_montant(self):
        """Test l'extraction du montant"""
        text_lines = ["Total à payer: 75000 GNF"]
        result = self.ocr.extract_edg_invoice_data(text_lines)
        self.assertEqual(result['montant'], 75000.0)

if __name__ == '__main__':
    unittest.main()
```

---

## 📊 Résultats Attendus

### Screen 1 (Inscription)
```json
{
  "success": true,
  "message": "Registration successful. Please login.",
  "user_id": 1
}
```

### Screen 2 (Login)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user_224620123456",
    "phone_number": "+224620123456",
    "kyc_invoice_verified": false
  }
}
```

### Screen 3 (Upload EDG)
```json
{
  "message": "Invoice processed successfully",
  "ocr_data": {
    "edg_invoice_data": {
      "nom": "Jean Dupont",
      "quartier": "Kaloum",
      "tranche": "Tranche 2",
      "tarification": "Résidentiel",
      "numero_compteur": "12345678",
      "conso_actuelle": 1250.5,
      "conso_precedente": 1100.0,
      "periode": "01/2024",
      "montant": 75000.0
    },
    "success": true
  },
  "kyc_status": "verified"
}
```

---

## 🛡️ Tests de Sécurité

### Téléphone invalide
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "123456", "date_of_birth": "1995-05-15", "password": "SecurePass123", "password_confirm": "SecurePass123"}'
# ❌ Phone number must start with +224
```

### Mineur (< 18 ans)
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+224620123456", "date_of_birth": "2010-05-15", "password": "SecurePass123", "password_confirm": "SecurePass123"}'
# ❌ You must be at least 18 years old
```

### Mot de passe faible
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+224620123456", "date_of_birth": "1995-05-15", "password": "weak", "password_confirm": "weak"}'
# ❌ Password must be at least 8 characters
```

---

*Créé : 2026-04-19*  
*Version : 1.0*
