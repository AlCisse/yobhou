# Flutter Assets - Instructions Complètes

## 📥 Téléchargement des Assets

### 1. Fonts Poppins (OBLIGATOIRE)

**Étapes :**
1. Allez sur : https://fonts.google.com/specimen/Poppins
2. Cliquez sur "Download family" (bouton en haut à droite)
3. Extrayez le ZIP téléchargé
4. Copiez les fichiers `.ttf` dans `assets/fonts/` :

```
assets/fonts/
├── Poppins-Regular.ttf      (weight: 400)
├── Poppins-Medium.ttf       (weight: 500)
├── Poppins-SemiBold.ttf     (weight: 600)
└── Poppins-Bold.ttf         (weight: 700)
```

**Vérification :**
```bash
cd flutter_app
ls -la assets/fonts/
# Doit afficher les 4 fichiers .ttf
```

### 2. Images (Recommandé pour production)

**Logo Yobhou :**
- Format : PNG transparent
- Taille : 512x512px minimum
- Emplacement : `assets/images/logo.png`

**Onboarding :**
- `assets/images/onboarding_1.png` (1080x1920px)
- `assets/images/onboarding_2.png` (1080x1920px)
- `assets/images/onboarding_3.png` (1080x1920px)

**Empty States :**
- `assets/images/empty_state.png` (512x512px)

**Alternative MVP :**
Si vous n'avez pas de designer, utilisez des icônes Material ou créez des placeholders avec Canva/Figma.

---

## 🔧 Après Ajout des Assets

```bash
cd flutter_app

# Nettoyer le cache
flutter clean

# Récupérer les dépendances
flutter pub get

# Générer les fichiers (si build_runner)
flutter pub run build_runner build --delete-conflicting-outputs

# Vérifier
flutter doctor

# Build APK
flutter build apk --release
```

---

## 📝 Notes

- Les fonts sont **obligatoires** pour que l'app compile
- Les images peuvent être des placeholders pour le MVP
- Taille totale des assets : < 10MB recommandé
- Formats supportés : PNG, JPG, SVG (avec flutter_svg)
