# Flutter Assets

## Required Assets

### Images (`assets/images/`)
- `logo.png` - Yobhou logo (512x512px, transparent background)
- `onboarding_1.png` - Onboarding screen 1 illustration
- `onboarding_2.png` - Onboarding screen 2 illustration
- `onboarding_3.png` - Onboarding screen 3 illustration
- `empty_state.png` - Empty state illustration for lists

### Fonts (`assets/fonts/`)
Download Poppins font from Google Fonts:
- `Poppins-Regular.ttf`
- `Poppins-Medium.ttf` (weight: 500)
- `Poppins-SemiBold.ttf` (weight: 600)
- `Poppins-Bold.ttf` (weight: 700)

**Download link:** https://fonts.google.com/specimen/Poppins

## After Adding Assets

Run:
```bash
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```
