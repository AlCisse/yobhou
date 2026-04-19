# 🔐 Architecture de Sécurité - Yobhou Fintech

## 🏦 Classification : Niveau Bancaire

Ce document définit l'architecture de sécurité conforme aux standards **BCEAO**, **PCI-DSS** (futur), et **RGPD-like**.

---

## 1. Chiffrement des Données

### 1.1 Données au Repos (At Rest)
| Type de donnée | Algorithme | Emplacement | Rotation |
|----------------|------------|-------------|----------|
| Mots de passe | Argon2id | PostgreSQL | N/A (hash) |
| Secrets Docker | AES-256-GCM | Docker Swarm | 90 jours |
| Photos compteur | AES-256-CBC | DigitalOcean Spaces | 365 jours |
| Logs d'audit | AES-256-GCM | S3 Glacier | 10 ans |
| Clés API | AES-256-GCM | HSM/Vault | 180 jours |

### 1.2 Données en Transit
- **TLS 1.3** obligatoire pour toutes les communications
- **HSTS** activé avec preload
- **Certificats** : Let's Encrypt (renouvellement auto 60 jours)
- **Cipher suites** : TLS_AES_256_GCM_SHA384 uniquement

### 1.3 Clés de Chiffrement
- **HSM** : AWS CloudHSM ou HashiCorp Vault (transit)
- **Envelope Encryption** : Clé maître HSM + clés de données
- **Rotation automatique** : Via cron jobs sécurisés

---

## 2. Authentification & Autorisation

### 2.1 Utilisateurs Finaux
- **JWT** avec expiration courte (15 min access, 7 jours refresh)
- **OTP SMS** pour validation transactions > 500k GNF
- **Biométrie** : Empreinte/FaceID (mobile)
- **2FA** : Obligatoire pour agents et admin

### 2.2 Staff & Admin
- **RBAC** (Role-Based Access Control) strict
- **Séparation des privilèges** : Dev ≠ Ops ≠ Admin ≠ Audit
- **Audit logging** : Toutes les actions admin journalisées

### 2.3 API & Services
- **mTLS** entre services backend
- **API Keys** avec rotation 180 jours
- **Rate limiting** : 100 req/min par utilisateur

---

## 3. Protection des Données

### 3.1 Données Personnelles (RGPD-like)
- **Minimisation** : Seules données strictement nécessaires
- **Consentement** : Explicite, granulaire, révocable
- **Droit à l'oubli** : Suppression sous 30 jours
- **Portabilité** : Export JSON/CSV sous 72h

### 3.2 Données Financières
- **Tokenisation** : Numéros de compte/tokenisés
- **Pseudonymisation** : IDs utilisateurs non réversibles
- **Ségrégation** : DB production ≠ DB test

### 3.3 Logs & Audit
- **Immuabilité** : Logs écrits en WORM (Write Once Read Many)
- **Horodatage** : NTP synchronisé + signature temporelle
- **Rétention** : 10 ans minimum (archive S3 Glacier)
- **Intégrité** : Hash SHA-256 + chaîne de confiance

---

## 4. Sécurité Infrastructure

### 4.1 Docker Swarm
```yaml
# Tous les containers sensibles
read_only: true
tmpfs:
  - /tmp
  - /var/run
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
```

### 4.2 Segmentation Réseau
| Réseau | Services | Accès |
|--------|----------|-------|
| `yobhou-frontend` | Traefik, Web | Public (80/443) |
| `yobhou-backend` | DB, Redis, OCR | Interne uniquement |
| `yobhou-secrets` | Vault, HSM | Admin uniquement |

### 4.3 Secrets Management
- **Docker Secrets** : Production
- **HashiCorp Vault** : Rotation + audit
- **Jamais dans** : Code, env vars, logs, git

---

## 5. Monitoring & Détection

### 5.1 Supervision
- **Prometheus** : Métriques temps réel
- **Grafana** : Dashboards ops
- **Alertmanager** : Alertes critiques (SMS/Email)

### 5.2 Détection d'Intrusion
- **Fail2Ban** : Protection brute-force
- **WAF** : Traefik middleware (rate limiting, IP blacklist)
- **SIEM** : ELK Stack + corrélations

### 5.3 Alertes Critiques
| Événement | Canal | Délai |
|-----------|-------|-------|
| Tentative intrusion > 10 | SMS + Email | Immédiat |
| Transaction > 1M GNF | Email + Dashboard | < 5 min |
| Erreur auth > 5/minute | Dashboard | < 1 min |
| DB down | SMS + Email | Immédiat |
| Backup échoué | Email | < 1h |

---

## 6. Plan de Reprise d'Activité (PRA)

### 6.1 Backup Strategy
| Donnée | Fréquence | Rétention | Stockage |
|--------|-----------|-----------|----------|
| PostgreSQL | 1h (WAL) + 1j (dump) | 30j + 10 ans | DO Spaces + Glacier |
| Photos | Réplication temps réel | 10 ans | DO Spaces + Glacier |
| Logs | Flux continu | 10 ans | ELK + Glacier |
| Config | Git (chaque commit) | Illimité | GitHub + backup local |

### 6.2 RTO/RPO
- **RPO (Perte max)** : 1 heure
- **RTO (Récupération)** : 4 heures

### 6.3 Procédure de Restauration
1. Alertes automatiques (Prometheus)
2. Bascule sur replica (si DB)
3. Restauration backup (si corruption)
4. Notification users (si > 1h downtime)
5. Post-mortem sous 48h

---

## 7. Conformité & Audit

### 7.1 Obligations Réglementaires
- **BCEAO** : Licence EME, plafonds, KYC
- **ANRDP Guinée** : Protection données personnelles
- **GIABA** : Lutte anti-blanchiment (AML)

### 7.2 Audit Externe
- **Pentest** : Annuel (cabinet certifié)
- **Audit code** : Avant chaque release majeure
- **Certification** : ISO 27001 (objectif 24 mois)

### 7.3 Documentation Obligatoire
- Registre des traitements
- Politique de sécurité (ce document)
- Procédures incident (PSI)
- Rapports d'audit annuels

---

## 8. Checklists de Déploiement

### 8.1 Pre-Production
- [ ] Pentest externe validé
- [ ] Audit code sécurisé
- [ ] Tests charge (10k users simultanés)
- [ ] PRA testé avec succès
- [ ] Secrets tous dans Vault/Docker Secrets
- [ ] Logs immuables configurés
- [ ] Alertes critiques testées

### 8.2 Production
- [ ] TLS 1.3 vérifié (SSL Labs A+)
- [ ] Rate limiting activé
- [ ] Backup automatique fonctionnel
- [ ] Monitoring 24/7 opérationnel
- [ ] On-call astreinte configurée
- [ ] Documentation ops à jour

---

*Document version : 1.0*
*Dernière mise à jour : 2026-04-19*
*Prochaine revue : 2026-07-19 (trimestrielle)*
