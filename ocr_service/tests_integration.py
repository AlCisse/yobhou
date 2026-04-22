# 🧪 TESTS INTEGRATION - OCR Service

"""
Tests d'intégration OCR avec images réelles reçues.
Ces tests nécessitent un environnement avec OpenCV installé.
"""

import pytest
import os
from decimal import Decimal

# Constants
FIXTURES_DIR = "fixtures/ocr_samples/"
CONFIDENCE_THRESHOLD = 0.85


class TestOCRSamples:
    """Tests OCR sur images réelles reçues"""

    @pytest.fixture(scope="class")
    def ocr_service(self):
        """Initialise le service OCR"""
        try:
            from ocr_service.paddle_ocr_wrapper import ocr_service
            return ocr_service
        except ImportError:
            pytest.skip("OCR service non disponible (OpenCV manquant)")

    def test_ocr_sample_1_file_0_jpg(self, ocr_service):
        """Test OCR sur première facture EDG reçue"""
        image_path = os.path.join(FIXTURES_DIR, "file_0---52fbadf8-241f-44cf-8bb9-b6ba27807ff2.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
            
        result = ocr_service.extract_text(image_path)
        
        assert result["success"] is True
        assert result["meter_number"] is not None
        assert isinstance(result["index"], (int, float, Decimal))
        assert result["confidence_scores"] is not None
        
        avg_confidence = sum(result["confidence_scores"]) / len(result["confidence_scores"])
        assert avg_confidence >= CONFIDENCE_THRESHOLD

    def test_ocr_sample_2_file_1_jpg(self, ocr_service):
        """Test OCR sur photo compteur reçue"""
        image_path = os.path.join(FIXTURES_DIR, "file_1---245f5987-58b8-42d0-b6c9-50e512b55a02.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
            
        result = ocr_service.extract_text(image_path)
        
        assert result["success"] is True
        assert result["meter_number"] is not None

    def test_ocr_sample_3_file_2_jpg(self, ocr_service):
        """Test OCR sur facture EDG claire"""
        image_path = os.path.join(FIXTURES_DIR, "file_2---f27b3504-ada9-419a-9d9a-2847c8920ac9.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
            
        result = ocr_service.extract_text(image_path)
        
        assert result["success"] is True
        assert result["index"] is not None
        assert result["index"] > 0

    def test_ocr_sample_4_file_3_jpg(self, ocr_service):
        """Test OCR sur image floue (seuil de confiance)"""
        image_path = os.path.join(FIXTURES_DIR, "file_3---89d3e5d6-87f0-4e45-bc7f-e5e3fb95a930.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
            
        result = ocr_service.extract_text(image_path)
        
        # Peut réussir ou échouer selon qualité
        if result["success"]:
            avg_confidence = sum(result["confidence_scores"]) / len(result["confidence_scores"])
            # Accepte confiance un peu plus basse pour images difficiles
            assert avg_confidence >= 0.75

    def test_ocr_sample_5_file_4_jpg(self, ocr_service):
        """Test OCR sur facture EDG typique"""
        image_path = os.path.join(FIXTURES_DIR, "file_4---3424aade-fdf4-4611-975b-a4e4fd0d33a8.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
            
        result = ocr_service.extract_text(image_path)
        
        assert result["success"] is True
        assert len(result["raw_text"]) > 0

    def test_ocr_confidence_threshold_validation(self, ocr_service):
        """Test validation seuil de confiance sur toutes les images"""
        fixture_files = [
            "file_0---52fbadf8-241f-44cf-8bb9-b6ba27807ff2.jpg",
            "file_1---245f5987-58b8-42d0-b6c9-50e512b55a02.jpg",
            "file_2---f27b3504-ada9-419a-9d9a-2847c8920ac9.jpg",
            "file_3---89d3e5d6-87f0-4e45-bc7f-e5e3fb95a930.jpg",
            "file_4---3424aade-fdf4-4611-975b-a4e4fd0d33a8.jpg"
        ]
        
        valid_count = 0
        for filename in fixture_files:
            image_path = os.path.join(FIXTURES_DIR, filename)
            if os.path.exists(image_path):
                result = ocr_service.extract_text(image_path)
                if result["success"]:
                    avg_confidence = sum(result["confidence_scores"]) / len(result["confidence_scores"])
                    if avg_confidence >= CONFIDENCE_THRESHOLD:
                        valid_count += 1
        
        # Au moins 80% des images doivent passer le seuil
        assert valid_count >= 4

    def test_ocr_multiple_languages_support(self, ocr_service):
        """Test support français dans OCR (lang='fr')"""
        # Vérifie que le service est initialisé avec langue française
        assert hasattr(ocr_service.ocr, 'lang')
        assert ocr_service.ocr.lang == 'fr'

    def test_ocr_edge_cases_corrupted_images(self, ocr_service):
        """Test gestion images corrompues ou vides"""
        # Création image vide fictive pour test
        empty_image_path = os.path.join(FIXTURES_DIR, "empty.jpg")
        if os.path.exists(empty_image_path):
            result = ocr_service.extract_text(empty_image_path)
            # Doit gérer gracieusement
            assert result["success"] is False or len(result["raw_text"]) == 0

    @pytest.mark.performance
    def test_ocr_performance_under_5_seconds(self, ocr_service):
        """Test performance OCR (< 5 secondes par image)"""
        import time
        image_path = os.path.join(FIXTURES_DIR, "file_0---52fbadf8-241f-44cf-8bb9-b6ba27807ff2.jpg")
        
        if not os.path.exists(image_path):
            pytest.skip("Image fixture manquante")
        
        start_time = time.time()
        result = ocr_service.extract_text(image_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Moins de 5 secondes
        assert result["success"] is True