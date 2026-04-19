#!/usr/bin/env python3
"""
Packager un skill pour Yobhou
Prépare un skill pour être partagé ou déployé
"""

import os
import sys
import zipfile
from pathlib import Path


def package_skill(project_root):
    """Packager un skill"""
    
    skill_path = project_root / "skills" / "SKILL.md"
    
    if not skill_path.exists():
        print(f"❌ Skill non trouvé : {skill_path}")
        sys.exit(1)
    
    # Créer le fichier zip
    zip_path = project_root / "skills" / "skill.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(skill_path, "SKILL.md")
    
    print(f"✅ Skill packagé : {zip_path}")


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    print(f"Packaging du skill dans : {project_root}")
    
    # Packager le skill
    package_skill(project_root)
    
    print("\n✅ Skill packagé avec succès !")


if __name__ == "__main__":
    main()