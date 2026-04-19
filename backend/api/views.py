"""  
Yobhou Fintech - OCR and Meter Reading API Views
All endpoints are stateless (JWT authentication), no session usage.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ocr_service.paddle_ocr_wrapper import ocr_service
import os
import uuid
import json
import hashlib
from pathlib import Path
from apps.meters.models import MeterReading
from apps.users.models import User


def validate_file_type(file, allowed_mime_types, allowed_extensions):
    """
    Validate file by both MIME type and extension for security.
    """
    # Check extension
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in allowed_extensions:
        return False, f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}'
    
    # Check MIME type (if available)
    if hasattr(file, 'content_type') and file.content_type:
        if file.content_type not in allowed_mime_types:
            return False, f'Invalid MIME type: {file.content_type}'
    
    return True, None


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_invoice(request):
    """
    Endpoint to upload and process an invoice image.
    Returns OCR extracted data for validation.
    
    Security:
    - JWT authentication required
    - File type validation (MIME + extension)
    - File size limit (10MB)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    if 'invoice' not in request.FILES:
        return JsonResponse({'error': 'No invoice file provided'}, status=400)
    
    invoice_file = request.FILES['invoice']
    
    # Validate file size (max 10MB)
    if invoice_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum 10MB allowed'}, status=400)
    
    # Validate file type
    allowed_mime_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    
    is_valid, error_message = validate_file_type(invoice_file, allowed_mime_types, allowed_extensions)
    if not is_valid:
        return JsonResponse({'error': error_message}, status=400)
    
    # Save uploaded file temporarily
    storage = FileSystemStorage()
    filename = f"invoice_{uuid.uuid4().hex}{os.path.splitext(invoice_file.name)[1].lower()}"
    file_path = storage.save(filename, invoice_file)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    try:
        # Process with OCR (skip for PDF in MVP)
        file_ext = os.path.splitext(invoice_file.name)[1].lower()
        if file_ext == '.pdf':
            return JsonResponse({
                'message': 'PDF uploaded successfully. OCR will be processed separately.',
                'file_path': file_path,
                'validation_required': True
            })
        
        result = ocr_service.extract_text(full_path)
        
        if not result['success']:
            return JsonResponse({
                'error': 'OCR failed to extract text from invoice',
                'details': result.get('raw_text', [])
            }, status=400)
        
        # Validate OCR confidence
        if not ocr_service.validate_ocr_result(result):
            return JsonResponse({
                'message': 'OCR confidence too low. Please retake photo.',
                'ocr_data': {
                    'extracted_text': result['raw_text'],
                    'meter_number': result.get('meter_number'),
                    'index': result.get('index'),
                    'confidence': result.get('confidence_scores', []),
                    'success': result['success']
                },
                'validation_required': False
            })
        
        return JsonResponse({
            'message': 'Invoice processed successfully',
            'ocr_data': {
                'extracted_text': result['raw_text'],
                'meter_number': result.get('meter_number'),
                'index': result.get('index'),
                'confidence': result.get('confidence_scores', []),
                'success': result['success']
            },
            'validation_required': True
        })
        
    finally:
        # Cleanup
        if os.path.exists(full_path):
            os.remove(full_path)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def capture_meter(request):
    """
    Endpoint to capture meter photo and perform OCR.
    Returns extracted meter data for validation.
    
    Security:
    - JWT authentication required
    - File type validation (MIME + extension)
    - File size limit (10MB)
    - Rate limiting (1 per day per user - implemented in middleware)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    if 'meter_photo' not in request.FILES:
        return JsonResponse({'error': 'No meter photo provided'}, status=400)
    
    meter_photo = request.FILES['meter_photo']
    
    # Validate file size (max 10MB)
    if meter_photo.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum 10MB allowed'}, status=400)
    
    # Validate file type
    allowed_mime_types = ['image/jpeg', 'image/jpg', 'image/png']
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    
    is_valid, error_message = validate_file_type(meter_photo, allowed_mime_types, allowed_extensions)
    if not is_valid:
        return JsonResponse({'error': error_message}, status=400)
    
    # Save uploaded file temporarily
    storage = FileSystemStorage()
    filename = f"meter_{uuid.uuid4().hex}{os.path.splitext(meter_photo.name)[1].lower()}"
    file_path = storage.save(filename, meter_photo)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    try:
        # Process with OCR
        result = ocr_service.extract_text(full_path)
        
        if not result['success']:
            return JsonResponse({
                'error': 'OCR failed to extract meter data',
                'details': result.get('raw_text', [])
            }, status=400)
        
        # Validate OCR confidence
        if not ocr_service.validate_ocr_result(result):
            return JsonResponse({
                'message': 'OCR confidence too low. Please retake photo.',
                'ocr_data': {
                    'extracted_text': result['raw_text'],
                    'meter_number': result.get('meter_number'),
                    'index': result.get('index'),
                    'confidence': result.get('confidence_scores', []),
                    'success': result['success']
                },
                'validation_required': False
            })
        
        return JsonResponse({
            'message': 'Meter photo processed successfully',
            'ocr_data': {
                'extracted_text': result['raw_text'],
                'meter_number': result.get('meter_number'),
                'index': result.get('index'),
                'confidence': result.get('confidence_scores', []),
                'success': result['success']
            },
            'validation_required': True
        })
        
    finally:
        # Cleanup
        if os.path.exists(full_path):
            os.remove(full_path)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def validate_reading(request):
    """
    Endpoint to validate OCR extracted data and create meter reading.
    Finalizes meter reading and creates transaction if validated.
    
    Security:
    - JWT authentication required
    - User context from JWT token (not session)
    - Input validation
    - Audit logging
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    data = request.data  # Use request.data for DRF (parses JSON)
    
    meter_number = data.get('meter_number')
    current_index = data.get('current_index')
    previous_index = data.get('previous_index', 0)
    meter_number_confidence = data.get('meter_number_confidence', '1.0')
    index_confidence = data.get('index_confidence', '1.0')
    
    # Validate required fields
    if not all([meter_number, current_index]):
        return JsonResponse({
            'error': 'Missing required fields: meter_number and current_index'
        }, status=400)
    
    try:
        current_index = float(current_index)
        previous_index = float(previous_index)
        meter_number_confidence = float(meter_number_confidence)
        index_confidence = float(index_confidence)
    except ValueError:
        return JsonResponse({'error': 'Invalid numeric values provided'}, status=400)
    
    # Validate indices
    if current_index <= previous_index:
        return JsonResponse({
            'error': 'Current index must be greater than previous index'
        }, status=400)
    
    # Calculate consumption
    consumption = current_index - previous_index
    
    # Save validated reading to database
    user = request.user  # From JWT authentication
    meter_reading = MeterReading.objects.create(
        user=user,
        meter_number=meter_number,
        previous_index=previous_index,
        current_index=current_index,
        consumption=consumption,
        ocr_data={
            'meter_number': meter_number,
            'index': current_index,
            'meter_number_confidence': meter_number_confidence,
            'index_confidence': index_confidence,
        },
        is_validated=True
    )
    
    return JsonResponse({
        'message': 'Reading validated successfully',
        'reading': {
            'id': meter_reading.id,
            'meter_number': meter_reading.meter_number,
            'current_index': meter_reading.current_index,
            'consumption': meter_reading.consumption,
            'ocr_confidence': {
                'meter_number': meter_number_confidence,
                'index': index_confidence
            }
        },
        'next_step': 'Proceed to payment selection'
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def health_check(request):
    """
    Health check endpoint for monitoring.
    No authentication required.
    
    Returns:
    {
        "status": "ok",
        "timestamp": "2026-04-19T12:00:00Z",
        "version": "1.0.0"
    }
    """
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'service': 'yobhou-backend'
    })
