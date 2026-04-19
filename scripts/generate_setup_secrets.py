#!/usr/bin/env python3
"""
Générateur de script de setup des secrets Docker pour Yobhou
Sécurité niveau fintech - Aucun secret en clair
"""

import os
import sys
from pathlib import Path


def generate_setup_secrets_script(project_root):
    """Génère le script de setup des secrets Docker"""
    
    script_content = """#!/bin/bash
# Script de configuration des Docker Secrets pour Yobhou
# RENDRE CE SCRIPT SECURISE : chmod 700 setup_secrets.sh
# CET SCRIPT DOIT ETRE EXECUTE AVANT TOUT DEPloiEMENT

set -e

echo "🔧 Configuration des Docker Secrets pour Yobhou"
echo "🔒 NIVEAU DE SECURITE : Fintech - DOCKER SECRETS OBLIGATOIRES"

# Créer le dossier secrets s'il n'existe pas
mkdir -p ./secrets

# Vérifier les permissions avant
if [ ! -d "./secrets" ]; then
    echo "❌ Le dossier ./secrets n'existe pas"
    exit 1
fi

# Générer les secrets si nécessaire
if [ ! -f ./secrets/django_secret_key ]; then
    echo "🔑 Génération de DJANGO_SECRET_KEY..."
    openssl rand -base64 64 > ./secrets/django_secret_key
    chmod 600 ./secrets/django_secret_key
fi

if [ ! -f ./secrets/orange_money_api_key ]; then
    echo "📱 Génération de ORANGE_MONEY_API_KEY..."
    openssl rand -base64 32 > ./secrets/orange_money_api_key
    chmod 600 ./secrets/orange_money_api_key
fi

if [ ! -f ./secrets/orange_money_shared_secret ]; then
    echo "🔐 Génération de ORANGE_MONEY_SHARED_SECRET..."
    openssl rand -base64 32 > ./secrets/orange_money_shared_secret
    chmod 600 ./secrets/orange_money_shared_secret
fi

if [ ! -f ./secrets/mtn_mobile_money_api_key ]; then
    echo "📱 Génération de MTN_MOBILE_MONEY_API_KEY..."
    openssl rand -base64 32 > ./secrets/mtn_mobile_money_api_key
    chmod 600 ./secrets/mtn_mobile_money_api_key
fi

if [ ! -f ./secrets/mtn_mobile_money_shared_secret ]; then
    echo "🔐 Génération de MTN_MOBILE_MONEY_SHARED_SECRET..."
    openssl rand -base64 32 > ./secrets/mtn_mobile_money_shared_secret
    chmod 600 ./secrets/mtn_mobile_money_shared_secret
fi

if [ ! -f ./secrets/qr_code_encryption_key ]; then
    echo "二维码 Génération de QR_CODE_ENCRYPTION_KEY..."
    openssl rand -base64 32 > ./secrets/qr_code_encryption_key
    chmod 600 ./secrets/qr_code_encryption_key
fi

if [ ! -f ./secrets/postgres_password ]; then
    echo "💾 Génération de POSTGRES_PASSWORD..."
    openssl rand -base64 32 > ./secrets/postgres_password
    chmod 600 ./secrets/postgres_password
fi

if [ ! -f ./secrets/postgres_super_password ]; then
    echo "👑 Génération de POSTGRES_SUPER_PASSWORD..."
    openssl rand -base64 32 > ./secrets/postgres_super_password
    chmod 600 ./secrets/postgres_super_password
fi

if [ ! -f ./secrets/traefik_cert ]; then
    echo "🔑 Génération de TRAEFIK_CERT..."
    openssl rand -base64 32 > ./secrets/traefik_cert
    chmod 600 ./secrets/traefik_cert
fi

if [ ! -f ./secrets/traefik_key ]; then
    echo "🔑 Génération de TRAEFIK_KEY..."
    openssl rand -base64 32 > ./secrets/traefik_key
    chmod 600 ./secrets/traefik_key
fi

# Vérifier les permissions
echo "✅ Permissions vérifiées pour tous les secrets"
chmod 600 ./secrets/*

# Afficher les fichiers créés
echo ""
echo "📁 Fichiers de secrets créés :"
ls -la ./secrets/
echo ""

echo "🔒 Configuration Docker Secrets terminée"
echo ""
echo "ℹ️  Important : Ce script DOIT être exécuté avec les bonnes permissions"
echo "ℹ️  Aucun secret ne doit être stocké en clair"
echo "ℹ️  Utiliser ce script avant 'docker stack deploy'"
echo "ℹ️  QR Code Integration : secrets/qr_code_encryption_key sera utilisé pour les paiements publics"
"""

    # Écrire le fichier
    script_path = project_root / "infrastructure" / "docker-swarm" / "setup_secrets.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Rendre le script exécutable
    os.chmod(script_path, 0o700)
    
    print(f"✅ Script généré : {script_path} (chmod 700)")


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python generate_setup_secrets.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"🔧 Génération du script setup_secrets.sh dans : {project_root}")
    
    # Générer le script
    generate_setup_secrets_script(project_root)
    
    print("\n✅ Script de setup des secrets généré avec succès !")
    print("\nNext steps :")
    print("1. Exécuter './infrastructure/docker-swarm/setup_secrets.sh'")
    print("2. Review les secrets générés dans ./secrets/")
    print("3. Déployer avec 'docker stack deploy -c docker-stack.yml yobhou'")


if __name__ == "__main__":
    main()