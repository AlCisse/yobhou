#!/bin/bash
# Yobhou Backend Setup Script
# This script initializes the Django backend

set -e

echo "🚀 Yobhou Backend Setup"
echo "======================="

# Create .env file from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual secrets before deploying!"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Generate migrations
echo "🗄️  Generating database migrations..."
python manage.py makemigrations users
python manage.py makemigrations meters
python manage.py makemigrations transactions

# Apply migrations (optional, skip in production if using separate migration step)
if [ "$1" == "--apply" ]; then
    echo "✅ Applying migrations..."
    python manage.py migrate
fi

# Create superuser (optional)
if [ "$1" == "--create-superuser" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual secrets"
echo "2. Run: python manage.py migrate"
echo "3. Run: python manage.py createsuperuser"
echo "4. Run: python manage.py runserver"
