#!/bin/bash
# Yobhou Flutter - Download Poppins Fonts
# Automatically downloads Poppins fonts from Google Fonts

set -e

echo "🔤 Downloading Poppins Fonts from Google Fonts"
echo "=============================================="

FONTS_DIR="assets/fonts"

# Create fonts directory if not exists
mkdir -p "$FONTS_DIR"

# Google Fonts CDN URLs for Poppins
POPPINS_BASE="https://github.com/google/fonts/raw/main/apache/poppins"

echo "📥 Downloading Poppins fonts..."

# Download Regular (400)
echo "  → Poppins-Regular.ttf"
curl -sL "$POPPINS_BASE/Poppins-Regular.ttf" -o "$FONTS_DIR/Poppins-Regular.ttf"

# Download Medium (500)
echo "  → Poppins-Medium.ttf"
curl -sL "$POPPINS_BASE/Poppins-Medium.ttf" -o "$FONTS_DIR/Poppins-Medium.ttf"

# Download SemiBold (600)
echo "  → Poppins-SemiBold.ttf"
curl -sL "$POPPINS_BASE/Poppins-SemiBold.ttf" -o "$FONTS_DIR/Poppins-SemiBold.ttf"

# Download Bold (700)
echo "  → Poppins-Bold.ttf"
curl -sL "$POPPINS_BASE/Poppins-Bold.ttf" -o "$FONTS_DIR/Poppins-Bold.ttf"

echo ""
echo "✅ Fonts downloaded successfully!"
echo ""
echo "📋 Verification:"
ls -lh "$FONTS_DIR"/*.ttf

echo ""
echo "🔧 Next steps:"
echo "1. flutter clean"
echo "2. flutter pub get"
echo "3. flutter build apk --release"
