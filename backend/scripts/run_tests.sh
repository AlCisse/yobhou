#!/bin/bash
# Yobhou Fintech - Run All Tests
# Exécute tous les tests backend avec rapport détaillé

set -e

echo "🧪 Yobhou Fintech - Test Suite"
echo "=============================="
echo ""

# Check if virtual environment is active
if [ ! -n "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not active!"
    echo "Run: python -m venv venv && source venv/bin/activate"
    exit 1
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-django pytest-cov factory-boy -q

echo ""
echo "🗂️  Running Tests by Category"
echo "=============================="
echo ""

# 1. User Model Tests
echo "👤 1. User Model & Auth Tests..."
pytest apps/users/tests.py -v --tb=short

echo ""

# 2. User Integration Tests
echo "🔌 2. API Integration Tests..."
pytest apps/users/tests_integration.py -v --tb=short

echo ""

# 3. Meter Reading Tests
echo "📏 3. Meter Reading Tests..."
pytest apps/meters/tests.py -v --tb=short

echo ""

# 4. Transaction & AML Tests
echo "💰 4. Transaction & AML Tests..."
pytest apps/transactions/tests.py -v --tb=short

echo ""

# 5. OCR Service Tests
echo "📸 5. OCR Service Tests..."
pytest ocr_service/tests.py -v --tb=short

echo ""
echo "✅ All Tests Complete!"
echo "====================="
echo ""

# Run full coverage report
echo "📊 Generating Coverage Report..."
pytest --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "📈 Coverage HTML report generated in: htmlcov/index.html"
echo ""
echo "🎉 Test Suite Finished!"
