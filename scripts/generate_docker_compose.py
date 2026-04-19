#!/usr/bin/env python3
"""
Générateur de configuration Docker Compose sécurisée pour Yobhou
Version avec Docker Secrets obligatoire et sécurité niveau fintech
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


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python generate_docker_compose.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"🔧 Génération de docker-compose.yml sécurisé dans : {project_root}")
    
    # Générer le fichier
    generate_secure_docker_compose(project_root)
    
    print("\n✅ Configuration Docker Compose sécurisée générée avec succès !")
    print("\nNext steps :")
    print("1. Exécuter './setup_secrets.sh' pour générer les secrets")
    print("2. Review les secrets générés dans ./secrets/")
    print("3. Déployer avec 'docker-compose up -d'")


if __name__ == "__main__":
    main()