# 🧪 Test du Scénario d'Inscription Yobhou

## 📋 Scénario de Test

### Screen 1 : Inscription
**Endpoint :** `POST /api/register/`

**Payload :**
```json
{
  "phone_number": "+224620123456",
  "date_of_birth": "1995-05-15",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}
```

**Réponse attendue :**
```json
{
  "success": true,
  "message": "Registration successful. Please login.",
  "user_id": 1
}
```

---

### Screen 2 : Login JWT
**Endpoint :** `POST /api/login/`

**Payload :**
```json
{
  "phone_number": "+224620123456",
  "password": "SecurePass123"
}
```

**Réponse attendue :**
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

---

### Screen 3 : Upload Facture EDG
**Endpoint :** `POST /api/upload-invoice/`

**Headers :**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body :** Image de la facture EDG (JPG/PNG)

**Réponse attendue :**
```json
{
  "message": "Invoice processed successfully",
  "ocr_data": {
    "extracted_text": ["EDG", "Facture N°...", ...],
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
    "meter_number": "12345678",
    "index": 1250.5,
    "confidence": [0.95, 0.92, ...],
    "success": true
  },
  "validation_required": true,
  "kyc_status": "verified"
}
```

---

## 🔧 Commandes de Test

### 1. Lancer le serveur de dev
```bash
cd /home/node/.openclaw/workspace/yobhou/backend
python3 manage.py runserver 0.0.0.0:8000
```

### 2. Tester l'inscription (Screen 1)
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+224620123456",
    "date_of_birth": "1995-05-15",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }'
```

### 3. Tester le login (Screen 2)
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_224620123456",
    "password": "SecurePass123"
  }'
```

### 4. Tester l'upload facture (Screen 3)
```bash
# Remplacer <access_token> par le token reçu au login
curl -X POST http://localhost:8000/api/upload-invoice/ \
  -H "Authorization: Bearer <access_token>" \
  -F "invoice=@/path/to/edg_invoice.jpg"
```

### 5. Vérifier le profil utilisateur
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer <access_token>"
```

---

## ✅ Checklist de Validation

- [ ] Inscription avec téléphone +224 valide
- [ ] Validation âge minimum (18 ans)
- [ ] Validation force du mot de passe
- [ ] Génération auto du username depuis le téléphone
- [ ] JWT token généré correctement
- [ ] OCR extrait tous les champs EDG :
  - [ ] nom
  - [ ] quartier
  - [ ] tranche
  - [ ] tarification
  - [ ] numero_compteur
  - [ ] conso_actuelle
  - [ ] conso_precedente
  - [ ] periode
  - [ ] montant
- [ ] Données EDG sauvegardées dans le profil utilisateur
- [ ] kyc_invoice_verified = true après upload

---

## 🛡️ Tests de Sécurité

### Injection de téléphone invalide
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "123456", "date_of_birth": "1995-05-15", "password": "SecurePass123", "password_confirm": "SecurePass123"}'
# Doit retourner : Phone number must start with +224
```

### Mot de passe faible
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+224620123456", "date_of_birth": "1995-05-15", "password": "weak", "password_confirm": "weak"}'
# Doit retourner : Password must be at least 8 characters
```

### Upload fichier non-image
```bash
curl -X POST http://localhost:8000/api/upload-invoice/ \
  -H "Authorization: Bearer <token>" \
  -F "invoice=@malicious.exe"
# Doit retourner : Invalid MIME type
```

---

*Document de test créé : 2026-04-19*  
*Version : 1.0*
