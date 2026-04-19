#!/usr/bin/env python3
"""
Générateur de projet Yobhou - Application de paiement factures EDG
Génère la structure complète du projet avec Flutter, Django et Docker Swarm
"""

import os
import sys
from pathlib import Path


def create_directory(path):
    """Crée un répertoire s'il n'existe pas"""
    path.mkdir(parents=True, exist_ok=True)
    print(f"Créé : {path}")


def generate_project_structure(project_root):
    """Génère la structure complète du projet Yobhou"""
    
    # Structure pour l'application mobile Flutter
    mobile_dir = project_root / "mobile"
    flutter_structure = {
        mobile_dir: [
            "pubspec.yaml",
            "lib/main.dart",
            "lib/services/payment_service.dart",
            "lib/services/bill_service.dart",
            "lib/models/bill.dart",
            "lib/models/payment.dart",
            "lib/pages/home_page.dart",
            "lib/pages/bill_detail_page.dart",
            "lib/pages/payment_page.dart",
            "lib/widgets/bill_item.dart",
            "android/app/src/main/AndroidManifest.xml",
            "ios/Runner/Info.plist",
        ],
        mobile_dir / "lib": [
            "main.dart",
            "services/",
            "models/",
            "pages/",
            "widgets/",
            "utils/",
            "providers/",
        ],
        mobile_dir / "lib" / "services": [
            "payment_service.dart",
            "bill_service.dart",
        ],
        mobile_dir / "lib" / "models": [
            "bill.dart",
            "payment.dart",
        ],
        mobile_dir / "lib" / "pages": [
            "home_page.dart",
            "bill_detail_page.dart",
            "payment_page.dart",
            "auth_page.dart",
        ],
        mobile_dir / "lib" / "widgets": [
            "bill_item.dart",
            "payment_method_selector.dart",
        ],
        mobile_dir / "lib" / "utils": [
            "constants.dart",
            "validators.dart",
        ],
        mobile_dir / "lib" / "providers": [
            "bill_provider.dart",
            "payment_provider.dart",
        ],
    }
    
    # Structure pour le backend Python
    backend_dir = project_root / "backend"
    python_structure = {
        backend_dir: [
            "requirements.txt",
            "docker-compose.yml",
            "entrypoint.sh",
            "manage.py",
            "config/",
            "apps/",
            "static/",
            "media/",
        ],
        backend_dir / "config": [
            "__init__.py",
            "settings.py",
            "urls.py",
            "wsgi.py",
            "celery.py",
        ],
        backend_dir / "apps": [
            "__init__.py",
            "billing/",
            "payments/",
            "customers/",
            "agencies/",
        ],
        backend_dir / "apps" / "billing": [
            "__init__.py",
            "models.py",
            "serializers.py",
            "views.py",
            "urls.py",
        ],
        backend_dir / "apps" / "payments": [
            "__init__.py",
            "models.py",
            "serializers.py",
            "views.py",
            "urls.py",
            "services.py",
        ],
        backend_dir / "apps" / "customers": [
            "__init__.py",
            "models.py",
            "serializers.py",
            "views.py",
            "urls.py",
        ],
        backend_dir / "apps" / "agencies": [
            "__init__.py",
            "models.py",
            "serializers.py",
            "views.py",
            "urls.py",
        ],
        backend_dir / "static": [],
        backend_dir / "media": [],
    }
    
    # Structure pour Docker Swarm
    swarm_dir = project_root / "infrastructure" / "docker-swarm"
    swarm_structure = {
        swarm_dir: [
            "docker-stack.yml",
            "traefik/",
            "postgres/",
            "redis/",
            "celery/",
            "monitoring/",
        ],
        swarm_dir / "traefik": [
            "traefik.yml",
            "configs/",
            "acme.json",
        ],
        swarm_dir / "postgres": [
            "init-scripts/",
            "volumes/",
        ],
        swarm_dir / "redis": ["volumes/"],
        swarm_dir / "celery": ["worker.sh", "beat.sh"],
        swarm_dir / "monitoring": [
            "prometheus.yml",
            "grafana-dashboard.yml",
        ],
    }
    
    # Structure complète à créer
    all_structures = [flutter_structure, python_structure, swarm_structure]
    
    for structure in all_structures:
        for directory, files in structure.items():
            create_directory(directory)
            for file_path in files:
                if isinstance(file_path, str):
                    file_path = directory / file_path
                create_directory(file_path.parent)
                # On ne crée pas les fichiers vides ici pour éviter la surcharge
                # Les fichiers réels seront générés séparément


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python generate_project.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"Génération du projet Yobhou dans : {project_root}")
    
    # Créer la structure
    generate_project_structure(project_root)
    
    print("\n✅ Structure de projet Yobhou générée avec succès !")
    print("\nNext steps :")
    print("1. Configurer les variables d'environnement")
    print("2. Lancer 'docker-compose up -d' pour le backend")
    print("3. Lancer 'flutter run' pour l'application mobile")


if __name__ == "__main__":
    main()