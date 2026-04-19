# Scripts de génération de projet Yobhou

Ce dossier contient les scripts pour générer la structure complète du projet Yobhou.

## Scripts disponibles

### `generate_project.py`
Génère la structure complète du projet Yobhou avec tous les dossiers nécessaires.

**Usage :**
```bash
python generate_project.py <project_root>
```

**Exemple :**
```bash
python generate_project.py /home/node/.openclaw/workspace/yobhou
```

## Conventions

- Tous les scripts doivent être exécutables
- Utiliser Python 3.10+ pour la compatibilité
- Suivre les bonnes pratiques de génération de code
- Créer une structure modulaire pour faciliter l'évolution

## Structure des scripts

Chaque script doit suivre cette structure :

```python
#!/usr/bin/env python3
"""Description du script"""

import os
import sys
from pathlib import Path

def main():
    """Fonction principale"""
    # Code du script

if __name__ == "__main__":
    main()
```

## Aide

Pour obtenir de l'aide sur un script, exécuter :
```bash
python script_name.py --help
```