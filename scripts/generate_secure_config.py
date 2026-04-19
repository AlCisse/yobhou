#!/usr/bin/env python3
"""
Secure configuration generator for Yobhou
Creates Docker Compose files with Docker Secrets integration and fintech-level security
"""

import os
import sys
from pathlib import Path


def generate_secure_docker_compose(project_root):
    """Génère docker-compose.yml sécurisé avec Docker Secrets"""
    
    compose_content = """version: '3.8'

services:
  # PostgreSQL - Database
  postgres:
    image: postgres:15-alpine
    secrets:
      - postgres_password
      - postgres_super_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      POSTGRES_SUPER_PASSWORD_FILE: /run/secrets/postgres_super_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - db_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

  # Redis - Cache
  redis:
    image: redis:7-alpine
    networks:
      - internal_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

  # Django Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    secrets:
      - django_secret_key
      - orange_money_api_key
      - orange_money_shared_secret
      - mtn_mobile_money_api_key
      - mtn_mobile_money_shared_secret
      - qr_code_encryption_key
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
      ORANGE_MONEY_API_KEY_FILE: /run/secrets/orange_money_api_key
      ORANGE_MONEY_SHARED_SECRET_FILE: /run/secrets/orange_money_shared_secret
      MTN_MOBILE_MONEY_API_KEY_FILE: /run/secrets/mtn_mobile_money_api_key
      MTN_MOBILE_MONEY_SHARED_SECRET_FILE: /run/secrets/mtn_mobile_money_shared_secret
      QR_CODE_ENCRYPTION_KEY_FILE: /run/secrets/qr_code_encryption_key
    depends_on:
      - postgres
      - redis
    networks:
      - frontend_network
      - backend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.celery
    secrets:
      - django_secret_key
      - orange_money_api_key
      - mtn_mobile_money_api_key
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
      ORANGE_MONEY_API_KEY_FILE: /run/secrets/orange_money_api_key
      MTN_MOBILE_MONEY_API_KEY_FILE: /run/secrets/mtn_mobile_money_api_key
    depends_on:
      - redis
      - postgres
    networks:
      - backend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

  # Celery Beat
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.celery
    secrets:
      - django_secret_key
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
    depends_on:
      - redis
      - postgres
    networks:
      - backend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

  # Traefik - Reverse Proxy
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=false"
      - "--providers.docker.swarmMode=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - type: bind
        source: /var/run/docker.sock
        target: /var/run/docker.sock
        read_only: true
    secrets:
      - traefik_cert
      - traefik_key
    networks:
      - frontend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    restart: unless-stopped

secrets:
  postgres_password:
    external: true
  postgres_super_password:
    external: true
  django_secret_key:
    external: true
  orange_money_api_key:
    external: true
  orange_money_shared_secret:
    external: true
  mtn_mobile_money_api_key:
    external: true
  mtn_mobile_money_shared_secret:
    external: true
  qr_code_encryption_key:
    external: true
  traefik_cert:
    external: true
  traefik_key:
    external: true

networks:
  frontend_network:
    driver: overlay
  backend_network:
    driver: overlay
    internal: true
  db_network:
    driver: overlay
    internal: true
  internal_network:
    driver: overlay
    internal: true

volumes:
  postgres_data:
"""

    # Écrire le fichier
    compose_path = project_root / "backend" / "docker-compose.yml"
    with open(compose_path, 'w') as f:
        f.write(compose_content)
    
    print(f"✅ Fichier généré : {compose_path}")


def generate_secure_docker_stack(project_root):
    """Génère docker-stack.yml pour Docker Swarm"""
    
    stack_content = """version: '3.8'

services:
  # PostgreSQL - Database
  postgres:
    image: postgres:15-alpine
    secrets:
      - postgres_password
      - postgres_super_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      POSTGRES_SUPER_PASSWORD_FILE: /run/secrets/postgres_super_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - db_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == manager

  # Redis - Cache
  redis:
    image: redis:7-alpine
    networks:
      - internal_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == manager

  # Django Backend
  backend:
    image: yobhou/backend:latest
    secrets:
      - django_secret_key
      - orange_money_api_key
      - orange_money_shared_secret
      - mtn_mobile_money_api_key
      - mtn_mobile_money_shared_secret
      - qr_code_encryption_key
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
      ORANGE_MONEY_API_KEY_FILE: /run/secrets/orange_money_api_key
      ORANGE_MONEY_SHARED_SECRET_FILE: /run/secrets/orange_money_shared_secret
      MTN_MOBILE_MONEY_API_KEY_FILE: /run/secrets/mtn_mobile_money_api_key
      MTN_MOBILE_MONEY_SHARED_SECRET_FILE: /run/secrets/mtn_mobile_money_shared_secret
      QR_CODE_ENCRYPTION_KEY_FILE: /run/secrets/qr_code_encryption_key
    depends_on:
      - postgres
      - redis
    networks:
      - frontend_network
      - backend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker

  # Celery Worker
  celery_worker:
    image: yobhou/celery:latest
    secrets:
      - django_secret_key
      - orange_money_api_key
      - mtn_mobile_money_api_key
    environment:
      DJANGO_SECRET_KEY_FILE: /run/secrets/django_secret_key
      ORANGE_MONEY_API_KEY_FILE: /run/secrets/orange_money_api_key
      MTN_MOBILE_MONEY_API_KEY_FILE: /run/secrets/mtn_mobile_money_api_key
    depends_on:
      - redis
      - postgres
    networks:
      - backend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Traefik - Reverse Proxy
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=false"
      - "--providers.docker.swarmMode=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - type: bind
        source: /var/run/docker.sock
        target: /var/run/docker.sock
        read_only: true
    secrets:
      - traefik_cert
      - traefik_key
    networks:
      - frontend_network
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:size=64M,mode=1777
    deploy:
      mode: global
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == manager

secrets:
  postgres_password:
    external: true
    file: ./secrets/postgres_password
  postgres_super_password:
    external: true
    file: ./secrets/postgres_super_password
  django_secret_key:
    external: true
    file: ./secrets/django_secret_key
  orange_money_api_key:
    external: true
    file: ./secrets/orange_money_api_key
  orange_money_shared_secret:
    external: true
    file: ./secrets/orange_money_shared_secret
  mtn_mobile_money_api_key:
    external: true
    file: ./secrets/mtn_mobile_money_api_key
  mtn_mobile_money_shared_secret:
    external: true
    file: ./secrets/mtn_mobile_money_shared_secret
  qr_code_encryption_key:
    external: true
    file: ./secrets/qr_code_encryption_key
  traefik_cert:
    external: true
    file: ./secrets/traefik_cert
  traefik_key:
    external: true
    file: ./secrets/traefik_key

networks:
  frontend_network:
    driver: overlay
  backend_network:
    driver: overlay
    internal: true
  db_network:
    driver: overlay
    internal: true
  internal_network:
    driver: overlay
    internal: true

volumes:
  postgres_data:
"""

    # Écrire le fichier
    stack_path = project_root / "infrastructure" / "docker-swarm" / "docker-stack.yml"
    with open(stack_path, 'w') as f:
        f.write(stack_content)
    
    print(f"✅ Fichier généré : {stack_path}")


def generate_secret_setup_script(project_root):
    """Génère le script de setup des secrets Docker"""
    
    script_content = """#!/bin/bash
# Script de configuration des Docker Secrets pour Yobhou
# RENDRE CE SCRIPT SECURISE : chmod 700 setup_secrets.sh

set -e

echo "🔧 Configuration des Docker Secrets pour Yobhou"

# Créer le dossier secrets s'il n'existe pas
mkdir -p ./secrets

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

echo "🔒 Configuration Docker Secrets terminée"
echo ""
echo "ℹ️  Important : Ce script DOIT être exécuté avec les bonnes permissions"
echo "ℹ️  Aucun secret ne doit être stocké en clair"
echo "ℹ️  Utiliser ce script avant 'docker stack deploy'"
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
        print("Usage: python generate_secure_config.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"🔧 Génération des configurations sécurisées dans : {project_root}")
    
    # Générer les fichiers
    generate_secure_docker_compose(project_root)
    generate_secure_docker_stack(project_root)
    generate_secret_setup_script(project_root)
    
    print("\n✅ Configuration sécurisée générée avec succès !")
    print("\nNext steps :")
    print("1. Exécuter 'cd infrastructure/docker-swarm && ./setup_secrets.sh'")
    print("2. Review les secrets générés dans ./secrets/")
    print("3. Déployer avec 'docker stack deploy -c docker-stack.yml yobhou'")


if __name__ == "__main__":
    main()