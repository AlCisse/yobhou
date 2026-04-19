#!/bin/bash
# Yobhou Database Initialization Script
# Creates migrations and applies them

set -e

echo "🗄️  Yobhou Database Initialization"
echo "==================================="

# Generate migrations for all apps
echo "📝 Generating migrations..."
python manage.py makemigrations users
python manage.py makemigrations meters
python manage.py makemigrations transactions

echo "✅ Migrations generated successfully!"
echo ""

# Apply migrations (optional - comment out if using separate migration step in production)
if [ "$1" == "--apply" ]; then
    echo "✅ Applying migrations..."
    python manage.py migrate
    echo "✅ Migrations applied successfully!"
    echo ""
fi

# Create superuser (optional)
if [ "$1" == "--create-superuser" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser
fi

echo "📋 Next steps:"
echo "1. python manage.py createsuperuser (if not done above)"
echo "2. python manage.py runserver (development)"
echo "3. OR docker stack deploy (production)"
