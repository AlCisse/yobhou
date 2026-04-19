# ROADMAP.md - Feuille de Route Technique Projet Yobhou (MVP Guinée)

## 🎯 Objectif Global
Livrer un MVP fonctionnel permettant aux usagers guinéens de scanner leur facture EDG, relever leur compteur électrique, et simuler un paiement via Mobile Money (OM/MTN) ou en agence physique. Le système doit être adaptable à la connectivité faible, sécurisé, et compatible avec les smartphones courants.

---

## 🗓️ Phases de Développement

### 🔹 Phase 1 : Backend Django (Serveur Central & OCR)

#### Durée estimée : 2 semaines

#### Modules à développer :
- **Authentification JWT** (`django-rest-framework-simplejwt`)
- **Modèles principaux** :
  - Utilisateur (profil, KYC léger)
  - Compteur (numéro, type, index, photo relevé)
  - Transaction (simulation Mobile Money, statut)
- **Service OCR basique** :
  - Intégration librairie OCR (Tesseract ou Google Vision API mockée)
  - Extraction champs : Numéro compteur, index, date, nom titulaire
- **Endpoints API publiques** :
  - Upload facture + réponse OCR structurée
  - Capture photo compteur + traitement OCR métiers
  - Validation manuelle utilisateur
- **Simulation Paiement Mobile Money** :
  - Webhook ping local pour tests
  - Endpoint de callback fake pour déclencher statuts paiements
- **Stockage sécurisé** :
  - Données sensibles via **Docker Secrets**
  - Photos temporaires chiffrées sur volume local

#### Technologies :
- Python 3.11+, Django 4.2, PostgreSQL, Redis
- Docker Swarm (déploiement futur)

#### Livrables :
- Documentation API swaggerisée
- Postman collection tests internes
- Collection de tests unitaires couvrant >= 80%

---

### 🔹 Phase 2 : Application Mobile Flutter (Frontend Utilisateur)

#### Durée estimée : 3 semaines

#### Fonctionnalités mobiles :
- **Flux Onboarding utilisateur** :
  - Inscription via téléphone + OTP (Africa’s Talking sandbox)
  - Upload ou capture caméra de la dernière facture EDG
  - OCR automatique + validation manuelle
- **Capture photo compteur** :
  - Interface caméra native Flutter avec guides visuels
  - Traitement image côté mobile (prétraitement OCR)
- **Validation finale** :
  - Affichage des données extraites
  - Boutons “Confirmer” ou “Recommencer”
- **Modes de paiement simulés** :
  - Option Mobile Money (Orange & MTN) – redirection vers stub
  - Option Paiement Agence – Génération QR code chiffré
- **Offline-first design** :
  - Sauvegarde locale photos/non-envoyées
  - Synchro automatique dès connectivité retrouvée

#### Technologies :
- Flutter 3.x, Riverpod, GoRouter, Dio
- Caméra + OCR Tesseract ou ML Kit (sans Firebase)

#### Livrables :
- APK fonctionnel (Android)
- IPA minimal (iOS si nécessaire)
- Tests widgets/intégration (> 70%)

---

### 🔹 Phase 3 : Intégration Notifications (WAHA + SMS Sandbox)

#### Durée estimée : 1 semaine

#### Canaux intégrés :
- **WhatsApp via WAHA** :
  - Container isolé avec accès REST API
  - Envoi message OTP + reçu paiement
- **SMS via Africa’s Talking Sandbox** :
  - Callback URL interne pour tracking messages sortants
- **Email secondaire** (activation optionnelle via admin)

#### Sécurité :
- Journalisation des notifications envoyées
- Filtrage par IP source pour WAHA API

#### Livrables :
- Service de notification abstrait
- Tests e2e basiques (stub/mocké)
- Documentation technique pour extension future (WhatsApp Business API)

---

### 🔹 Phase 4 : Infrastructure Dockerisée & CI/CD

#### Durée estimée : 1 semaine

#### Tâches :
- **Dockerisation complète** :
  - Backend Django + WAHA + PostgreSQL + Redis
  - Secrets exclusivement dans **Docker Secrets**
- **Read-only containers** pour services sensibles
- **Traefik reverse proxy** pour routage HTTPS interne
- **Pipeline GitHub Actions** :
  - Linting Python/Flutter
  - Tests automatisés
  - Build images Docker + push registry privé

#### Sécurité :
- Politique réseau stricte entre services
- Rotation automatique des secrets Docker (cron/gitops)

#### Livrables :
- docker-stack.yml fonctionnel
- CI/CD GitHub Actions configurée
- Script déploiement staging/production

---

### 🔹 Phase 5 : Tests & Packaging MVP

#### Durée estimée : 1 semaine

#### Activités :
- Tests end-to-end (OCR → Paiement simulé)
- Test UX sur terminaux milieu de gamme
- Packaging final APK temporaire
- Setup serveur de staging accessible

#### Livrables :
- APK installable (distribution privée initiale)
- Rapport couverture tests
- Manuel utilisation interne (PDF)

---

### 🔹 Phase 6 : Plan Marketing Pilote & Dashboard EDG

#### Durée estimée : 1 semaine

#### Actions :
- Campagne pilote à Conakry (zone choisie)
- Recrutement testeurs volontaires (anonymisés)
- Suivi des performances : nombre scans/jour, taux réussite OCR
- Dashboard admin simple :
  - Vue liste relevés validés
  - Export CSV pour EDG
  - Statistiques basiques (par zone/date)

#### Livrables :
- Dashboard admin Flask/Django minimal
- Rapport testeurs pilotes
- Présentation PowerPoint pitch MVP + prochaines étapes

---

## 📆 Planning Global Estimé

| Phase                                 | Durée |
|--------------------------------------|-------|
| Backend Django                       | 2 semaines |
| Application Mobile Flutter           | 3 semaines |
| Intégration Notifications            | 1 semaine |
| Infrastructure Docker & CI/CD        | 1 semaine |
| Tests & Packaging                    | 1 semaine |
| Plan Marketing Pilote + Dashboard EDG| 1 semaine |
| **Total**                            | **~9 semaines** |

---

## 🛠️ Technologies Clés Adoptées

- **Backend** : Python, Django, PostgreSQL, Redis, JWT
- **Mobile** : Flutter, Riverpod, Dio, Caméra native
- **Infrastructure** : Docker Swarm, Traefik, Docker Secrets
- **Notifications** : WAHA (WhatsApp), Africa’s Talking (SMS)
- **CI/CD** : GitHub Actions
- **Stockage** : DigitalOcean Spaces S3-Compatible
- **Sécurité** : AES-256, HTTPS/TLS 1.3, HMAC sur requêtes sensibles

---

📝 *Cette roadmap reste modifiable selon feedback technique ou changement stratégique.*