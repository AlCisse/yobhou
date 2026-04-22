# 🔐 SECURITY_ADVANCED.md - Niveau Bancaire Yobhou

**Date** : 2026-04-22  
**Version** : 1.0  
**Niveau** : Bancaire (PCI-DSS, ISO 27001, BCEAO)

---

## 📋 Objectifs de Sécurité

### Priorités
1. ✅ **Authentification forte** (2FA + Biometric)
2. ✅ **Chiffrement HSM** (Hardware Security Module)
3. ✅ **Anti-fraude IA** (Behavioral analytics)
4. ✅ **Audit blockchain** (Logs immuables)
5. ✅ **Monitoring SIEM** (Real-time + Forensics)

---

## 🔐 PHASE 1 : Authentification Avancée

### 1.1 2FA TOTP (Django OTP)

#### Installation
```bash
pip install django-otp django-two-factor-auth
```

#### Configuration `settings.py`
```python
INSTALLED_APPS += [
    'django_otp',
    'django_otp.plugins.otp_totp',
    'two_factor',
]

MIDDLEWARE += [
    'django_otp.middleware.OTPMiddleware',
]

# 2FA Settings
TWO_FACTOR_PHONE_NUMBER = 'phone_number'
TWO_FACTOR_TOTP_ISSUER = 'Yobhou'
TWO_FACTOR_REMEMBER_ME_DAYS = 7
```

#### URLs `urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as two_factor_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include(two_factor_urls)),
] + urlpatterns
```

#### Migration
```bash
python manage.py migrate
```

### 1.2 Biometric Mobile (Flutter)

#### Backend : Device Fingerprinting
```python
# core/models.py
class DeviceFingerprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=50)
    device_name = models.CharField(max_length=100)
    fingerprint_hash = models.CharField(max_length=64)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'device_id')
```

#### Serializer
```python
# users/serializers.py
from rest_framework import serializers

class DeviceFingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFingerprint
        fields = ['device_id', 'device_type', 'device_name', 'fingerprint_hash']
```

### 1.3 Session Management
```python
# settings.py
SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Inactivity timeout
SESSION_TIMEOUT_WARNING = 600  # 10 minutes
SESSION_TIMEOUT_FORCE_LOGOUT = 900  # 15 minutes
```

---

## 🔐 PHASE 2 : Chiffrement HSM

### 2.1 HashiCorp Vault Container

#### Docker Compose
```yaml
# docker-compose.hsm.yml
version: '3.8'
services:
  vault:
    image: vault:latest
    ports:
      - "8200:8200"
    volumes:
      - vault-storage:/vault/data
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=hsm-root-token-123
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    cap_add:
      - IPC_LOCK
    restart: unless-stopped

volumes:
  vault-storage:
```

#### Configuration Django
```python
# settings.py
import os
import hvac

# Vault Client
VAULT_ADDR = os.environ.get('VAULT_ADDR', 'http://vault:8200')
VAULT_TOKEN = os.environ.get('VAULT_TOKEN')

vault_client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

def get_secret_from_vault(key):
    """Récupérer secret depuis Vault"""
    try:
        secret = vault_client.read(f'secret/data/{key}')
        return secret['data']['data']['value']
    except Exception:
        return None

# Encryption Key (rotation 90 jours)
ENCRYPTION_KEY = get_secret_from_vault('encryption_key')
```

### 2.2 Key Rotation
```python
# core/key_rotation.py
from datetime import datetime, timedelta
from django.utils import timezone

def needs_key_rotation():
    """Vérifie si rotation nécessaire (90 jours)"""
    last_rotation = settings.LAST_KEY_ROTATION
    return timezone.now() > last_rotation + timedelta(days=90)

def rotate_encryption_key():
    """Rotation des clés"""
    from cryptography.fernet import Fernet
    
    # Nouvelle clé
    new_key = Fernet.generate_key()
    
    # Ré-encrypter tous les secrets
    # ... (logic détaillée)
    
    # Mise à jour timestamp
    settings.LAST_KEY_ROTATION = timezone.now()
```

### 2.3 Chiffrement Bout-en-Bout
```python
# core/encryption.py
from cryptography.fernet import Fernet

class EndToEndEncryption:
    def __init__(self, encryption_key):
        self.fernet = Fernet(encryption_key)
    
    def encrypt(self, data):
        """Chiffrement données"""
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        """Déchiffrement données"""
        return self.fernet.decrypt(encrypted_data).decode()
```

### 2.4 Signature Numérique
```python
# core/signature.py
import hmac
import hashlib

class DigitalSignature:
    @staticmethod
    def sign_transaction(transaction_data, secret_key):
        """Signer transaction"""
        message = str(transaction_data).encode()
        signature = hmac.new(
            secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(transaction_data, signature, secret_key):
        """Vérifier signature"""
        expected = DigitalSignature.sign_transaction(transaction_data, secret_key)
        return hmac.compare_digest(expected, signature)
```

---

## 🔐 PHASE 3 : Anti-Fraude IA

### 3.1 Geo-Blocking
```python
# core/geo_blocking.py
import requests

class GeoBlocking:
    RESTRICTED_COUNTRIES = [
        'KP',  # Corée du Nord
        'IR',  # Iran
        'SY',  # Syrie
        'CU',  # Cuba
    ]
    
    def check_location(self, ip_address):
        """Vérifier emplacement IP"""
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}')
            data = response.json()
            
            if data['countryCode'] in self.RESTRICTED_COUNTRIES:
                return {'blocked': True, 'reason': 'Pays restreint'}
            
            return {'blocked': False, 'country': data['country']}
        except Exception:
            return {'blocked': False, 'error': 'IP lookup failed'}
```

### 3.2 Velocity Checks
```python
# core/velocity_check.py
from django.utils import timezone
from datetime import timedelta

class VelocityCheck:
    @staticmethod
    def check_transaction_velocity(user_id, limit_per_hour=5):
        """Vérifier vitesse transactions"""
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        recent_transactions = Transaction.objects.filter(
            user_id=user_id,
            created_at__gte=one_hour_ago
        ).count()
        
        if recent_transactions > limit_per_hour:
            return {
                'velocity_alert': True,
                'count': recent_transactions,
                'limit': limit_per_hour
            }
        
        return {'velocity_alert': False}
    
    @staticmethod
    def check_device_switch(user_id, max_switches_per_day=3):
        """Vérifier changements devices"""
        from core.models import DeviceFingerprint
        
        today = timezone.now().date()
        
        device_count = DeviceFingerprint.objects.filter(
            user_id=user_id,
            created_at__date=today
        ).values('device_id').distinct().count()
        
        if device_count > max_switches_per_day:
            return {
                'device_switch_alert': True,
                'count': device_count
            }
        
        return {'device_switch_alert': False}
```

### 3.3 Behavioral Analytics
```python
# ml/behavioral_analytics.py
from sklearn.ensemble import IsolationForest
import numpy as np

class BehaviorAnalyzer:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01)
        self.trained = False
    
    def train_user_profile(self, user_id, transactions_data):
        """Apprendre profil utilisateur"""
        # Extraire features (montant, fréquence, heure, etc.)
        features = self._extract_features(transactions_data)
        
        self.model.fit(features)
        self.trained = True
    
    def _extract_features(self, transactions):
        """Extraire features from transactions"""
        features = []
        for txn in transactions:
            feature = [
                txn['amount'],
                txn['frequency_per_day'],
                txn['hour_of_day'],
                txn['is_night_transaction'],
                txn['is_weekend'],
            ]
            features.append(feature)
        return np.array(features)
    
    def detect_anomaly(self, user_id, new_transaction):
        """Détecter anomaly"""
        if not self.trained:
            return {'anomaly': False, 'confidence': 0}
        
        features = self._extract_features([new_transaction])
        prediction = self.model.predict(features)[0]
        score = self.model.decision_function(features)[0]
        
        return {
            'anomaly': prediction == -1,
            'confidence': abs(score),
            'score': score
        }
```

### 3.4 Sanctions Lists
```python
# core/sanctions_lists.py
import requests

class SanctionsCheck:
    # OFAC, EU, UN sanctions lists
    SANCTIONS_API = 'https://api sanctionslist.gov/check'
    
    def check_entity(self, entity_name):
        """Vérifier against sanctions lists"""
        try:
            response = requests.post(self.SANCTIONS_API, json={
                'name': entity_name,
                'type': 'individual'  # or 'entity'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('match'):
                    return {
                        'sanctions_alert': True,
                        'list': data['list'],
                        'score': data['score']
                    }
            
            return {'sanctions_alert': False}
        except Exception:
            return {'sanctions_alert': False, 'error': 'API unavailable'}
```

---

## 🔐 PHASE 4 : Audit Blockchain

### 4.1 Immutable Audit Log
```python
# core/blockchain_audit.py
import hashlib
import json
from datetime import datetime

class ImmutableAuditLog:
    def __init__(self):
        self.chain = []
        self.pending_blocks = []
    
    def add_log(self, data):
        """Ajouter log (hash chainé)"""
        block = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'prev_hash': self.chain[-1]['hash'] if self.chain else '0' * 64,
        }
        
        # Calculer hash
        block['hash'] = hashlib.sha256(
            json.dumps(block, sort_keys=True).encode()
        ).hexdigest()
        
        # Ajouter à chaîne
        self.chain.append(block)
        self._persist(block)
        
        return block
    
    def _persist(self, block):
        """Persistance (database + S3)"""
        # 1. Database (PostgreSQL)
        AuditLogEntry.objects.create(
            hash=block['hash'],
            prev_hash=block['prev_hash'],
            data=json.dumps(block['data']),
            timestamp=block['timestamp']
        )
        
        # 2. S3 Glacier (archive 10 ans)
        s3_client.put_object(
            Bucket='yobhou-audit-logs',
            Key=f'blocks/{block["hash"]}.json',
            Body=json.dumps(block)
        )
    
    def verify_integrity(self):
        """Vérifier intégrité chaîne"""
        for i in range(1, len(self.chain)):
            if self.chain[i]['prev_hash'] != self.chain[i-1]['hash']:
                return False
        return True
```

### 4.2 Timestamping
```python
# core/timestamping.py
import hashlib

class TimestampingService:
    @staticmethod
    def create_timestamp(data):
        """Créer timestamp IPFS-like"""
        data_str = str(data).encode()
        return hashlib.sha256(data_str).hexdigest()
    
    @staticmethod
    def verify_timestamp(original_data, timestamp):
        """Vérifier timestamp"""
        expected = TimestampingService.create_timestamp(original_data)
        return expected == timestamp
```

### 4.3 Forensics Toolkit
```python
# core/forensics.py
from datetime import datetime

class ForensicsTool:
    def __init__(self):
        self.evidence = []
    
    def collect_evidence(self, event_type, user_id, details):
        """Collecter preuves"""
        evidence = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'chain_link': self.evidence[-1]['hash'] if self.evidence else None
        }
        
        # Hash chain
        evidence['hash'] = hashlib.sha256(
            str(evidence).encode()
        ).hexdigest()
        
        self.evidence.append(evidence)
        return evidence
    
    def reconstruct_event(self, user_id, start_time, end_time):
        """Reconstruire événement"""
        return [
            ev for ev in self.evidence
            if ev['user_id'] == user_id
            and start_time <= ev['timestamp'] <= end_time
        ]
```

---

## 🔐 PHASE 5 : Monitoring SIEM

### 5.1 Real-Time Dashboard
```python
# core/monitoring.py
from prometheus_client import Counter, Gauge, Histogram

# Metrics
api_requests_total = Counter('api_requests_total', 'Total API requests')
api_requests_duration = Histogram('api_requests_duration', 'API request duration')
active_users = Gauge('active_users', 'Active users')

# Alerts
class AlertManager:
    CRITICAL_ALERTS = {
        'db_down': 'Database connection lost',
        'high_error_rate': 'Error rate > 5%',
        'aml_alert': 'AML alert detected',
    }
    
    @staticmethod
    def send_alert(alert_type, details):
        """Envoyer alerte"""
        if alert_type in AlertManager.CRITICAL_ALERTS:
            # SMS + Email + Dashboard
            notify.send_sms(alert_type, details)
            notify.send_email(alert_type, details)
            notify.update_dashboard(alert_type, details)
```

### 5.2 SIEM Integration
```python
# core/siem.py
import requests

class SIEMIntegration:
    def __init__(self, elasticsearch_url):
        self.es_url = elasticsearch_url
    
    def send_log(self, log_data):
        """Envoyer log à ELK"""
        response = requests.post(
            f'{self.es_url}/logs/_doc',
            json=log_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 201
```

---

## 📊 Résultat Final Sécurité

### Avant
```
Sécurité : Niveau Fintech
- JWT (15 min / 7 jours)
- AML checker (5 détecteurs)
- Docker secrets
- TLS 1.3
- Audit 10 ans
```

### Après
```
Sécurité : Niveau Bancaire ✅
- 2FA TOTP + Biometric
- HSM + Rotation 90 jours
- Chiffrement bout-en-bout
- Signature numérique
- Geo-blocking
- Velocity checks
- Behavioral analytics
- Sanctions lists
- Audit blockchain
- SIEM + Forensics
```

---

## ⏱️ État d'Avancement

| Tâche | Status |
|-------|--------|
| Authentification Avancée | 🟡 En cours |
| Chiffrement HSM | ⏳ Planifié |
| Anti-Fraude IA | ⏳ Planifié |
| Audit Blockchain | ⏳ Planifié |
| Monitoring SIEM | ⏳ Planifié |

**Total** : 0/13h complétées

---

## 🚀 Prochaine Étape

Souhaitez-vous que je continue :
1. ✅ **Phase 1** : Authentification avancée (2FA + Biometric)
2. 🔐 **Phase 2** : Chiffrement HSM (Vault + Rotation)
3. 🤖 **Phase 3** : Anti-fraude IA (Behavioral analytics)

Quelle phase prioritaires, Al ?