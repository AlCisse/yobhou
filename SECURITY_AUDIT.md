# Audit de Sécurité Yobhou - Rapport et Corrections

## Résumé Exécutif

Audit de sécurité complet réalisé sur le projet Yobhou (fintech de paiement d'électricité en Guinée). Les vulnérabilités critiques ont été corrigées.

---

## Vulnérabilités Corrigées

### 1. CRITIQUE - SECRET_KEY et Configuration Django

**Fichier:** `backend/core/settings.py`

**Problèmes:**
- `SECRET_KEY` avec valeur par défaut insecure
- `DEBUG=True` par défaut en production
- Headers de sécurité manquants (HSTS, CSP, X-Frame-Options)

**Corrections appliquées:**
```python
# SECRET_KEY obligatoire en production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY and not DEBUG:
    raise ValueError("SECRET_KEY must be set in production")

# DEBUG=False par défaut
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# Security headers (HSTS, CSP, etc.)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
```

---

### 2. CRITIQUE - Rate Limiting sur Endpoints Sensibles

**Fichier:** `backend/core/middleware.py` (nouveau)

**Problème:** Pas de protection contre les attaques par brute-force sur `/api/login/`, `/api/complete-registration/`

**Correction:** Middleware de rate limiting implémenté:
- `/api/complete-registration/`: 5 attempts/heure
- `/api/login/`: 10 attempts/heure
- `/api/verify-otp/`: 3 attempts/heure
- `/api/register/`: 3 attempts/heure

---

### 3. CRITIQUE - Énumération d'Utilisateurs

**Fichier:** `backend/api/views.py`

**Problème:** Message d'erreur différent selon si le phone_number existe ou non

**Correction:**
```python
# Validation stricte du format téléphone
if not re.match(r'^\+224\d{9}$', phone_number):
    return Response({'error': 'Numéro de téléphone invalide'}, status=400)

# Message générique pour prévenir l'énumération
if not users.exists():
    return Response({'error': 'Données invalides'}, status=400)
```

---

### 4. ÉLEVÉ - Validation Magic Bytes pour Uploads

**Fichier:** `backend/api/views.py`

**Problème:** Validation MIME type uniquement, vulnérable au MIME spoofing

**Correction:**
```python
# Validation magic bytes
header = file.read(8)
if file_ext == '.png' and not header.startswith(b'\x89PNG'):
    return False, 'Invalid PNG file (magic bytes mismatch)'
if file_ext in ['.jpg', '.jpeg'] and not header.startswith(b'\xff\xd8\xff'):
    return False, 'Invalid JPEG file (magic bytes mismatch)'
if file_ext == '.pdf' and not header.startswith(b'%PDF'):
    return False, 'Invalid PDF file (magic bytes mismatch)'
```

---

### 5. MOYEN - Thread-Safety OCR Service

**Fichier:** `backend/ocr_service/paddle_ocr_wrapper.py`

**Problème:** Instance globale partagée entre threads

**Correction:**
```python
# Thread-local storage
_local = threading.local()

def get_ocr_service() -> PaddleOCRService:
    if not hasattr(_local, 'ocr'):
        _local.ocr = PaddleOCRService()
    return _local.ocr
```

---

### 6. MOYEN - JWT Token Rotation

**Fichier:** `backend/core/settings.py`

**Correction:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

### 7. MOYEN - Flutter: SSL Pinning

**Fichier:** `flutter_app/lib/core/network/api_client.dart`

**Correction:** Interceptor SSL ajouté avec validation de certificat et détection d'expiration.

---

### 8. MOYEN - Flutter: Secure Storage

**Fichier:** `flutter_app/lib/features/auth/data/repositories/auth_repository_impl.dart`

**Correction:** Configuration de `FlutterSecureStorage` avec:
- Android Keystore (encryptedSharedPreferences)
- iOS Keychain (KeychainAccessibility.first_unlock_this_device)

---

## Fichiers Modifiés

| Fichier | Type de Correction |
|---------|-------------------|
| `backend/core/settings.py` | SECRET_KEY, DEBUG, Security Headers, JWT Rotation |
| `backend/core/middleware.py` | Rate Limiting (nouveau) |
| `backend/api/views.py` | Anti-énumération, Magic Bytes validation |
| `backend/ocr_service/paddle_ocr_wrapper.py` | Thread-safety |
| `flutter_app/lib/core/network/api_client.dart` | SSL Pinning |
| `flutter_app/lib/core/constants/app_constants.dart` | API URL config, SSL flags |
| `flutter_app/lib/features/auth/data/repositories/auth_repository_impl.dart` | Secure Storage |

---

## Recommandations Supplémentaires

### À implémenter avant production:

1. **Génération SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Docker Secrets:** Utiliser Docker Secrets au lieu de .env pour les credentials

3. **2FA (Double Authentification):**
   - Implémenter TOTP pour transactions > 500k GNF
   - Utiliser `pyotp` + Google Authenticator

4. **Token Blacklist Redis:**
   ```python
   # backend/core/settings.py
   SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] = True
   ```
   Nécessite `djangorestframework-simplejwt[redis]`

5. **Monitoring:**
   - Activer les logs de sécurité dans ELK
   - Alerts sur les tentatives rate-limit dépassées

6. **Backup & Recovery:**
   - Backup automatique PostgreSQL
   - Plan de reprise d'activité

---

## Conformité

- **BCEAO:** Limites 1M/5M GNF implémentées dans `aml_checker.py`
- **GIABA:** Détection structuring implémentée
- **Audit Trail:** Logs dans `logs/audit.log` (10 ans de rétention)

---

## Prochaines Étapes

1. Tester le backend avec `docker-compose -f docker-compose.dev.yml up`
2. Vérifier que le rate limiting fonctionne (tester 6 connexions successives)
3. Valider les uploads avec magic bytes
4. Déployer en staging avec variables d'environnement sécurisées
