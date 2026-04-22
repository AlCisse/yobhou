✅ **Option 1 : Tests via Docker Compose (Recommandé)**



🔧 **Avantages :**
- Tous les services isolés (PostgreSQL, Redis)
- Dépendances compilées dans container
- Tests complets exécutables

🔄 **Durée estimée :** 5-10 minutes

---

🐳 **Option 2 : Déploiement Docker Swarm Complet**



🌐 **Services déployés :**
- Web (2 replicas)
- DB PostgreSQL
- Redis
- OCR Worker
- Traefik (reverse proxy)

🔄 **Durée estimée :** 15-20 minutes

---

🧩 **Option 3 : Workaround PyMuPDF (Local)**

Bloquant actuel :
```
Building wheel for PyMuPDF (pyproject.toml): still running...
```

Solutions possibles :
1. Exclure `paddleocr` des requirements de test
2. Utiliser version allégée de PaddleOCR
3. Simuler dépendance PyMuPDF

⚠️ Plus complexe, risque de casser OCR.

---

📋 **Recommendation :**
Commencer par **Option 1** (Docker Compose dev) pour valider tests, puis passer à **Option 2** (Swarm) pour déploiement production.

Quel chemin choisis-tu, Al ?
