"""
Yobhou Fintech - OCR Service Unit Tests
Tests for PaddleOCR wrapper functionality
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal


class TestPaddleOCRService:
    """Tests for PaddleOCR wrapper"""
    
    @pytest.fixture
    def ocr_service(self):
        """Create OCR service instance (mocked)"""
        with patch('ocr_service.paddle_ocr_wrapper.PaddleOCR'):
            from ocr_service.paddle_ocr_wrapper import PaddleOCRService
            return PaddleOCRService()
    
    def test_extract_meter_number_valid(self, ocr_service):
        """Test meter number extraction from OCR results"""
        text_lines = [
            'FACTURE EAU ELECTRICITE',
            'Compteur: 12345678',
            'Index: 450 kWh',
            'Date: 01/2024'
        ]
        
        meter_number = ocr_service.extract_meter_number(text_lines)
        
        assert meter_number == '12345678'
        assert len(meter_number) == 8
    
    def test_extract_meter_number_not_found(self, ocr_service):
        """Test when no meter number is found"""
        text_lines = [
            'FACTURE EAU ELECTRICITE',
            'Nom: Dupont',
            'Adresse: Conakry'
        ]
        
        meter_number = ocr_service.extract_meter_number(text_lines)
        
        assert meter_number is None
    
    def test_extract_index_valid(self, ocr_service):
        """Test index extraction from OCR results"""
        text_lines = [
            'Compteur: 12345678',
            'Index actuel: 450.5 kWh',
            'Previous: 400.0'
        ]
        
        index = ocr_service.extract_index(text_lines)
        
        assert index == 450.5
    
    def test_extract_index_integer(self, ocr_service):
        """Test index extraction with integer value"""
        text_lines = [
            'Index: 450',
            'kWh'
        ]
        
        index = ocr_service.extract_index(text_lines)
        
        assert index == 450.0
    
    def test_extract_index_out_of_range(self, ocr_service):
        """Test that out-of-range values are rejected"""
        text_lines = [
            'Invalid: 999999999999',  # Too large
            'Negative: -100'  # Negative
        ]
        
        index = ocr_service.extract_index(text_lines)
        
        # Should return None for invalid values
        assert index is None
    
    def test_validate_ocr_result_success(self, ocr_service):
        """Test OCR result validation with good confidence"""
        result = {
            'success': True,
            'confidence_scores': [0.95, 0.92, 0.88],
            'meter_number': '12345678',
            'index': 450.0
        }
        
        is_valid = ocr_service.validate_ocr_result(result)
        
        assert is_valid is True
    
    def test_validate_ocr_result_low_confidence(self, ocr_service):
        """Test OCR result validation with low confidence"""
        result = {
            'success': True,
            'confidence_scores': [0.65, 0.70, 0.60],  # Below 0.8 threshold
            'meter_number': '12345678',
            'index': 450.0
        }
        
        is_valid = ocr_service.validate_ocr_result(result)
        
        assert is_valid is False
    
    def test_validate_ocr_result_no_success(self, ocr_service):
        """Test OCR result validation when success is False"""
        result = {
            'success': False,
            'confidence_scores': [],
            'error': 'OCR failed'
        }
        
        is_valid = ocr_service.validate_ocr_result(result)
        
        assert is_valid is False
    
    def test_validate_ocr_result_empty_confidence(self, ocr_service):
        """Test OCR result validation with empty confidence scores"""
        result = {
            'success': True,
            'confidence_scores': [],
            'meter_number': '12345678'
        }
        
        is_valid = ocr_service.validate_ocr_result(result)
        
        assert is_valid is False
    
    @patch('ocr_service.paddle_ocr_wrapper.cv2')
    @patch('ocr_service.paddle_ocr_wrapper.os')
    def test_preprocess_image_called(self, mock_os, mock_cv2, ocr_service):
        """Test that image preprocessing is called"""
        mock_image = MagicMock()
        mock_cv2.imread.return_value = mock_image
        mock_cv2.cvtColor.return_value = mock_image
        mock_cv2.GaussianBlur.return_value = mock_image
        mock_cv2.adaptiveThreshold.return_value = mock_image
        mock_cv2.fastNlMeansDenoising.return_value = mock_image
        
        ocr_service.preprocess_image('/fake/path/image.jpg')
        
        mock_cv2.imread.assert_called_once()
        mock_cv2.cvtColor.assert_called_once()


class TestOCRIntegration:
    """Integration tests for OCR service"""
    
    @pytest.mark.skip(reason="Requires actual PaddleOCR model")
    def test_full_ocr_pipeline(self):
        """Test complete OCR pipeline with real image"""
        # This test requires actual PaddleOCR installation
        # and a sample meter image
        pass
    
    @pytest.mark.skip(reason="Requires actual PaddleOCR model")
    def test_ocr_with_real_meter_photo(self):
        """Test OCR with real meter photo"""
        # This test requires sample meter photos
        pass


class TestOCRErrorHandling:
    """Test OCR error handling"""
    
    @patch('ocr_service.paddle_ocr_wrapper.PaddleOCR')
    def test_ocr_service_initialization(self, mock_paddleocr):
        """Test OCR service initializes correctly"""
        from ocr_service.paddle_ocr_wrapper import PaddleOCRService
        
        service = PaddleOCRService()
        
        assert service.ocr is not None
        mock_paddleocr.assert_called_once()
    
    @patch('ocr_service.paddle_ocr_wrapper.cv2')
    def test_preprocess_image_file_not_found(self, mock_cv2, ocr_service):
        """Test preprocessing with non-existent file"""
        mock_cv2.imread.return_value = None
        
        with pytest.raises(Exception):
            ocr_service.preprocess_image('/nonexistent/path/image.jpg')
