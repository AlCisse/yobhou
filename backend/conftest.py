"""
Pytest configuration for Yobhou backend tests.
Mocks OCR dependencies to avoid paddleocr import errors.
"""
import pytest
from unittest.mock import MagicMock

# Mock paddleocr before any imports
@pytest.fixture(autouse=True)
def mock_ocr_dependencies():
    """Mock OCR dependencies for all tests"""
    import sys
    sys.modules['paddleocr'] = MagicMock()
    sys.modules['paddlepaddle'] = MagicMock()
