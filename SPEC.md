# SPEC.md - Spécifications Projet Yobhou (Guinée)

## 📘 Nom du Projet
**Yobhou – Paiement Factures Électricité en Guinée**

## 🌍 Contexte Pays
Ce projet cible spécifiquement les usagers des fournisseurs d’énergie en **Guinée**, avec des adaptations légales locales et compatibilités avec les infrastructures mobiles locales.

## 🎯 Objectif Général
Permettre aux usagers de payer leurs factures d’électricité via :
- Mobile Money (Orange Money, MTN MoMo),
- Agences physiques équipées d’appareils de scan QR,
- Via application mobile fluide et performante même en zones rurales à faible connectivité.

## 👥 Acteurs Principaux
- **Client Final** : Utilisateur lambda payant sa facture EDG.
- **Agent Agence EDG/Yobhou** : Valide paiement en agence via scan QR/code client.
- **Administrateur Back Office** : Supervise transactions, gère comptes utilisateurs.
- **Opérateurs Mobile Money (OM, MTN)** : Intégration API sécurisée.
- **EDG (Entreprise de Distribution d'Électricité)** : Partenaire institutionnel clé.

## 🔐 Exigences Sécurité & Conformité
- **Chiffrement AES-256** des données sensibles
- **HTTPS/TLS 1.3** obligatoire pour toutes les communications externes
- **Signature des requêtes API paiement** (HMAC/JWT)
- **Protection anti-abus** :
  - Limite de relevé par jour
  - Contrôle cohérence IP/GPS
- **Journalisation complète** (logs immuables)
- **RGPD/Protection données** : Consentement explicite

## 📸 OCR & Traitement d'Image
- **Prétraitement** : Correction luminosité, bordures, perspective
- **Dataset personnalisé** : Collection de factures réelles EDG
- **Fallback** : Saisie manuelle si confiance OCR inférieure à 85 %

## 📡 Intégrations Externes
- **EDG** :
  - API officielle (si disponible) ou scraping sécurisé (légalité vérifiée)
- **Mobile Money** :
  - Sandboxes OM/MTN obligatoires avant mise en prod
- **SMS Notifications** :
  - API locale (Guinée Télécom ou partenaire fiable)
- **Offline Mode** :
  - Données sauvegardées localement si pas de réseau
  - Synchro différée dès connexion rétablie

## 🧾 Fonctionnalités Détaillées

### 🔑 Authentification & Onboarding Intelligent
- **Inscription Téléphone + OTP** (via Twilio/Africa’s Talking/local)
- **Scan Upload Facture EDG** :
  - Extraction OCR du numéro de compteur, nom titulaire, période, index kWh
  - Vérification âge de la facture (< 4 mois)
- **Validation Manuel Préalable** par utilisateur avant enregistrement
- **Données Utilisateur** :
  - Nom complet, email (optionnel), photo profil (optionnel)
  - Localisation estimée via adresse de la facture (quartier/préfecture)
  - Date de naissance saisie manuelle
- **KYC Léger** :
  - Selfie + pièce d'identité (CNI/Passeport Guinéen)
  - Vérification biométrique basique (facultatif)

### 🔍 Enregistrement Compteur (Onboarding Métier)
- **Interface Caméra Flutter** avec guides visuels (alignement automatique)
- **OCR Professionnel** :
  - Reconnaissance des chiffres mécaniques/numériques
  - Extraction index actuel (kWh)
  - Typologie compteur (prépayé vs postpayé)
- **Contrôle Anti-Fraude** :
  - Comparaison photo vs données enregistrées
  - Analyse EXIF pour détecter captures d’écran
- **Validation Finale** : Bouton "Valider" ou "Recommencer"

### 💰 Modes de Paiement Multi-Canaux
- **Dans l’application mobile** :
  - Orange Money Guinée (API REST)
  - MTN Mobile Money Guinée (API MoMo Collect)
  - Carte Bancaire (Stripe/PayDunya – secondaire)
- **En agence physique** :
  - Le client présente le QR code ou numéro de facture
  - L’agent Yobhou scanne le QR ou saisit le numéro
  - Envoi OTP via SMS/WA au client
  - Agent saisit le code reçu → Encaissement en liquide
  - Confirmation transaction + accusé de réception envoyé au client
- **Paiement Direct en Agence EDG** :
  - Génération code de paiement à présenter en agence (partenariat en cours)

### 📊 Tableau de Bord Utilisateur Avancé
- **Consommation en Temps Réel** :
  - Graphique évolutif mensuel
  - Comparaison vs moyenne quartier anonymisée
  - Prédiction de facture (ML simple)
- **Historique Transactions** :
  - Liste détaillée des relevés + photos archivées
  - Statut des factures (payées, en attente, échouées)
  - Téléchargement PDF factures officielles

### 🧮 Informations Tarifaires & Éducatives
- **Tarification EDG Officielle** (mise à jour automatique via webhook)
- **Simulateur de Consommation** :
  - Estimation mensuelle selon appareils électriques
  - Budget personnel configurable → Alertes si dépassement

### 🌍 Localisation & Assistance Locale
- **Cartographie des Agences EDG** :
  - Lieux disponibles (Conakry, Labé, Nzérékoré…)
  - Horaires d’ouverture + contact
  - Navigation GPS intégrée
- **Support Client Localisé** :
  - Chatbot multilingue (Français/Anglais)
  - Escalade via WhatsApp Business (si autorisé par EDG)

## 🇬🇳 Spécificités Contextuelles Guinée
- Multilingue : Français + Anglais
- Bas débit réseau pris en charge (interface responsive rapide)
- Caméras milieu de gamme supportées
- Montants en Francs Guinéens (GNF) avec précision décimale

## 📦 Livrables Attendus
- **Application Mobile Flutter** :
  - APK/IPA natifs optimisés pour Android/iOS
  - Interface fluide, adaptée à la bande passante variable
- **Backend Python Django** :
  - API RESTful documentée (Swagger/OpenAPI)
  - Webhooks sécurisés pour notifications paiement
- **Panneau Admin Django/React** :
  - Visualisation et validation manuelle des relevés suspects
- **Documentation Technique Complète** :
  - Guide déploiement (Docker Swarm + Docker Secrets)
  - Manuels d’intégration Mobile Money Guinée
  - Spécifications OCR pour formats EDG

## 📅 Dates Clés & Milestones
À définir ultérieurement dans `ROADMAP.md`.
