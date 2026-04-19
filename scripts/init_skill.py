#!/usr/bin/env python3
"""
Initialisation de la structure de projet Yobhou
Crée les dossiers et fichiers de base pour un nouveau projet
"""

import os
import sys
from pathlib import Path


def create_file(path, content=""):
    """Crée un fichier avec le contenu spécifié"""
    path.write_text(content)
    print(f"Créé : {path}")


def init_skill(project_root):
    """Initialise un nouveau skill"""
    
    # Créer les dossiers
    create_directory(project_root / "skills")
    
    # Créer le fichier SKILL.md
    skill_content = """---
name: your-new-skill
description: Description of your skill
---

# Your Skill Name

Description of what your skill does.
"""
    
    create_file(project_root / "skills" / "SKILL.md", skill_content)
    
    print("✅ Skill initialisé avec succès !")


def create_directory(path):
    """Crée un répertoire s'il n'existe pas"""
    path.mkdir(parents=True, exist_ok=True)
    print(f"Créé : {path}")


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python init_skill.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"Initialisation du skill dans : {project_root}")
    
    # Initialiser le skill
    init_skill(project_root)
    
    print("\n✅ Skill initialisé avec succès !")


if __name__ == "__main__":
    main()