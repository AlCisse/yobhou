from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from ocr_service.paddle_ocr_wrapper import ocr_service
import os
import uuid
from pathlib import Path


@csrf_exempt
def upload_invoice(request):
    """
    Endpoint to upload and process an invoice image.
    Returns OCR extracted data for validation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    if 'invoice' not in request.FILES:
        return JsonResponse({'error': 'No invoice file provided'}, status=400)
    
    invoice_file = request.FILES['invoice']
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    file_ext = os.path.splitext(invoice_file.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return JsonResponse({'error': 'Invalid file type. Allowed: JPG, JPEG, PNG, PDF'}, status=400)
    
    # Save uploaded file temporarily
    storage = FileSystemStorage()
    filename = f"invoice_{uuid.uuid4().hex}{file_ext}"
    file_path = storage.save(filename, invoice_file)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    try:
        # Process with OCR
        result = ocr_service.extract_text(full_path)
        
        if not result['success']:
            return JsonResponse({
                'error': 'OCR failed to extract text from invoice',
                'details': result.get('raw_text', [])
            }, status=400)
        
        # Save OCR result in session or temp storage for validation step
        request.session['invoice_ocr_result'] = result
        
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


@csrf_exempt
def capture_meter(request):
    """
    Endpoint to capture meter photo and perform OCR.
    Returns extracted meter data for validation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    if 'meter_photo' not in request.FILES:
        return JsonResponse({'error': 'No meter photo provided'}, status=400)
    
    meter_photo = request.FILES['meter_photo']
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    file_ext = os.path.splitext(meter_photo.name)[1].lower()
    
    if file_ext not in allowed_extensions:
        return JsonResponse({'error': 'Invalid file type. Allowed: JPG, JPEG, PNG'}, status=400)
    
    # Save uploaded file temporarily
    storage = FileSystemStorage()
    filename = f"meter_{uuid.uuid4().hex}{file_ext}"
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
        
        # Save OCR result for validation
        request.session['meter_ocr_result'] = result
        
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


@csrf_exempt
def validate_reading(request):
    """
    Endpoint to validate OCR extracted data.
    Finalizes meter reading and creates transaction if validated.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    data = request.POST
    
    meter_number = data.get('meter_number')
    current_index = data.get('current_index')
    meter_number_confidence = data.get('meter_number_confidence', '1.0')
    index_confidence = data.get('index_confidence', '1.0')
    
    # Validate required fields
    if not all([meter_number, current_index]):
        return JsonResponse({
            'error': 'Missing required fields: meter_number and current_index'
        }, status=400)
    
    try:
        current_index = float(current_index)
        meter_number_confidence = float(meter_number_confidence)
        index_confidence = float(index_confidence)
    except ValueError:
        return JsonResponse({'error': 'Invalid numeric values provided'}, status=400)
    
    # Save validated reading to database (mock implementation)
    # In real implementation, you would save to MeterReading model
    validated_reading = {
        'meter_number': meter_number,
        'current_index': current_index,
        'ocr_confidence': {
            'meter_number': meter_number_confidence,
            'index': index_confidence
        },
        'validated': True
    }
    
    return JsonResponse({
        'message': 'Reading validated successfully',
        'reading': validated_reading,
        'next_step': 'Proceed to payment selection'
    })