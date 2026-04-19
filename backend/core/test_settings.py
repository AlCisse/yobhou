"""
Django settings for running tests
"""
from .settings import *

# Use SQLite in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable logging during tests
LOGGING = {}

# Disable password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Use MD5 password hasher for speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug
DEBUG = False

# Mock OCR service for tests (avoid paddleocr import)
class MockOCRService:
    def extract_text(self, image_path):
        return {'success': True, 'raw_text': [], 'meter_number': None, 'index': None}
    def validate_ocr_result(self, result):
        return True

# Replace the real OCR service with mock
import sys
from unittest.mock import MagicMock
sys.modules['paddleocr'] = MagicMock()
sys.modules['paddlepaddle'] = MagicMock()
