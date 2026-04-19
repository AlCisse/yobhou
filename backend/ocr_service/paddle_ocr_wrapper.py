"""
PaddleOCR wrapper service for Yobhou project.

This module provides a simple interface to perform OCR on meter readings and invoices.
Uses PaddleOCR (Python binding) with optimized models for document extraction.
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import cv2
import numpy as np
from paddleocr import PaddleOCR


class PaddleOCRService:
    """Wrapper for PaddleOCR with preprocessing and postprocessing."""

    def __init__(self):
        # Initialize PaddleOCR with French language support
        self.ocr = PaddleOCR(
            lang='fr',
            use_angle_cls=True,
            det_db_score_mode='fast',
            det_db_shrink_ratio=0.5,
        )
        self.allowed_chars = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -._/@')

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        Includes: grayscale, thresholding, denoising, and deskewing.
        """
        # Load image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        threshold = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoising
        denoised = cv2.fastNlMeansDenoising(threshold, h=10)
        
        return denoised

    def extract_meter_number(self, text_lines: List[str]) -> Optional[str]:
        """Extract meter number from OCR results (typically 6-10 digits)."""
        for line in text_lines:
            # Look for patterns like "12345678" or "123456-78"
            import re
            match = re.search(r'\b\d{6,10}\b', line)
            if match:
                return match.group()
        return None

    def extract_index(self, text_lines: List[str]) -> Optional[float]:
        """Extract meter index (kWh) from OCR results."""
        for line in text_lines:
            import re
            # Look for decimal numbers like "12345.67" or "12345"
            matches = re.findall(r'\b\d+\.\d+\b|\b\d+\b', line)
            for match in matches:
                try:
                    value = float(match)
                    # Meter index is typically between 0 and 99999999
                    if 0 <= value <= 99999999:
                        return value
                except ValueError:
                    continue
        return None

    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Perform OCR on the image and extract relevant fields.
        Returns structured data with extracted information and confidence scores.
        """
        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        
        # Save temporarily for PaddleOCR
        temp_path = "/tmp/processed_ocr.jpg"
        cv2.imwrite(temp_path, processed_image)
        
        try:
            # Perform OCR
            result = self.ocr.ocr(temp_path, cls=True)
            
            # Extract text lines
            text_lines = []
            confidences = []
            
            if result and len(result) > 0:
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    text_lines.append(text)
                    confidences.append(confidence)
            
            # Extract specific fields
            meter_number = self.extract_meter_number(text_lines)
            index = self.extract_index(text_lines)
            
            return {
                "raw_text": text_lines,
                "confidence_scores": confidences,
                "meter_number": meter_number,
                "index": index,
                "success": len(text_lines) > 0,
            }
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def validate_ocr_result(self, result: Dict[str, Any], confidence_threshold: float = 0.8) -> bool:
        """
        Validate if OCR result meets minimum confidence requirements.
        Returns True if result is acceptable, False otherwise.
        """
        if not result.get("success", False):
            return False
        
        confidences = result.get("confidence_scores", [])
        if not confidences:
            return False
        
        avg_confidence = sum(confidences) / len(confidences)
        return avg_confidence >= confidence_threshold


# Global instance for reuse
ocr_service = PaddleOCRService()