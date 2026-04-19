import pytest
from django.contrib.auth import get_user_model
from apps.meters.models import MeterReading
from decimal import Decimal
import json

User = get_user_model()


@pytest.mark.django_db
class TestMeterReadingModel:
    def test_create_meter_reading(self):
        user = User.objects.create_user(
            username='testuser',
            phone_number='+224601234567',
            password='testpass123'
        )
        
        reading = MeterReading.objects.create(
            user=user,
            meter_number='12345678',
            previous_index=400.0,
            current_index=450.0,
            consumption=50.0,
            ocr_data={
                'raw_text': ['12345678', '450 kWh'],
                'confidence_scores': [0.95, 0.92]
            }
        )
        
        assert reading.meter_number == '12345678'
        assert reading.consumption == 50.0
        assert reading.is_validated == False
        assert reading.ocr_data['meter_number'] == '12345678'
    
    def test_consumption_calculation(self):
        user = User.objects.create_user(
            username='testuser2',
            phone_number='+224601234568',
            password='testpass123'
        )
        
        reading = MeterReading.objects.create(
            user=user,
            meter_number='87654321',
            previous_index=300.0,
            current_index=500.0,
            consumption=200.0,
            ocr_data={}
        )
        
        assert reading.current_index - reading.previous_index == reading.consumption
    
    def test_meter_reading_str(self):
        user = User.objects.create_user(
            username='testuser3',
            phone_number='+224601234569',
            password='testpass123'
        )
        
        reading = MeterReading.objects.create(
            user=user,
            meter_number='11111111',
            previous_index=100.0,
            current_index=150.0,
            consumption=50.0,
            ocr_data={}
        )
        
        assert '11111111' in str(reading)
        assert user.username in str(reading)


@pytest.mark.django_db
class TestMeterReadingValidation:
    def test_validate_reading(self):
        user = User.objects.create_user(
            username='testuser4',
            phone_number='+224601234570',
            password='testpass123'
        )
        
        reading = MeterReading.objects.create(
            user=user,
            meter_number='22222222',
            previous_index=200.0,
            current_index=250.0,
            consumption=50.0,
            ocr_data={'confidence': 0.88}
        )
        
        assert not reading.is_validated
        reading.is_validated = True
        reading.save()
        assert reading.is_validated
    
    def test_ocr_data_storage(self):
        user = User.objects.create_user(
            username='testuser5',
            phone_number='+224601234571',
            password='testpass123'
        )
        
        ocr_data = {
            'raw_text': ['22222222', '250 kWh', '01/2024'],
            'meter_number': '22222222',
            'index': 250.0,
            'confidence_scores': [0.95, 0.92, 0.88],
            'success': True
        }
        
        reading = MeterReading.objects.create(
            user=user,
            meter_number='22222222',
            previous_index=200.0,
            current_index=250.0,
            consumption=50.0,
            ocr_data=ocr_data
        )
        
        assert reading.ocr_data['success'] == True
        assert reading.ocr_data['meter_number'] == '22222222'
