"""
Tests unitaires pour le module de paiement
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.payments.models import Payment
from apps.payments.services.mobile_money import MobileMoneyService
from apps.payments.services.receipt_generator import ReceiptGenerator
from apps.meters.models import MeterReading


User = get_user_model()


@pytest.fixture
def user():
    """Créer un utilisateur test"""
    return User.objects.create_user(
        username='testuser',
        phone_number='+224612345678',
        password='testpass123'
    )


@pytest.fixture
def meter_reading(user):
    """Créer un relevé test"""
    return MeterReading.objects.create(
        user=user,
        meter_number='12345678',
        current_index=1250.5,
        previous_index=1100.0,
        consumption=150.5
    )


class TestPaymentModel:
    """Tests pour le modèle Payment"""
    
    def test_payment_creation(self, user, meter_reading):
        """Test création paiement"""
        payment = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678'
        )
        
        assert payment.transaction_reference.startswith('YBH-')
        assert payment.status == 'PENDING'
        assert payment.amount == Decimal('150000.00')
    
    def test_payment_str(self, user, meter_reading):
        """Test représentation string"""
        payment = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678'
        )
        
        assert str(payment) == f'Payment {payment.transaction_reference} - PENDING'
    
    def test_payment_reference_unique(self, user, meter_reading):
        """Test unicité référence"""
        Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678'
        )
        
        # Deuxième paiement doit avoir une référence différente
        payment2 = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('200000.00'),
            payment_method='MTN_MOMO',
            payment_phone='+224612345678'
        )
        
        assert Payment.objects.count() == 2
        assert Payment.objects.first().transaction_reference != Payment.objects.last().transaction_reference


class TestMobileMoneyService:
    """Tests pour le service Mobile Money"""
    
    def test_initiate_orange_money(self):
        """Test initiation Orange Money"""
        service = MobileMoneyService()
        result = service.initiate_payment(
            phone='+224612345678',
            amount=150000.00,
            reference='YBH-TEST-123',
            payment_method='ORANGE_MONEY'
        )
        
        assert result['success'] is True
        assert result['status'] == 'PENDING'
        assert 'OM-' in result['operator_reference']
    
    def test_initiate_mtn_momo(self):
        """Test initiation MTN MoMo"""
        service = MobileMoneyService()
        result = service.initiate_payment(
            phone='+224612345678',
            amount=150000.00,
            reference='YBH-TEST-456',
            payment_method='MTN_MOMO'
        )
        
        assert result['success'] is True
        assert result['status'] == 'PENDING'
        assert 'MOMO-' in result['operator_reference']
    
    def test_invalid_payment_method(self):
        """Test méthode invalide"""
        service = MobileMoneyService()
        
        with pytest.raises(ValueError):
            service.initiate_payment(
                phone='+224612345678',
                amount=150000.00,
                reference='YBH-TEST-789',
                payment_method='INVALID'
            )
    
    def test_verify_payment(self):
        """Test vérification paiement"""
        service = MobileMoneyService()
        result = service.verify_payment(
            operator_reference='OM-TEST-123',
            payment_method='ORANGE_MONEY'
        )
        
        assert result['success'] is True
        assert result['status'] == 'SUCCESS'


class TestReceiptGenerator:
    """Tests pour le générateur de reçu"""
    
    def test_generate_pdf(self, user, meter_reading):
        """Test génération PDF"""
        payment = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='COMPLETED',
            completed_at=timezone.now()
        )
        
        pdf_bytes = ReceiptGenerator.generate_pdf(payment)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'  # Header PDF
    
    def test_pdf_content(self, user, meter_reading):
        """Test contenu du PDF"""
        payment = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='COMPLETED',
            completed_at=timezone.now()
        )
        
        pdf_bytes = ReceiptGenerator.generate_pdf(payment)
        
        # Vérifier que le PDF contient les informations
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'YOBHOU' in pdf_text
        assert 'Reçu de Paiement' in pdf_text
        assert payment.transaction_reference in pdf_text


class TestPaymentAPI:
    """Tests pour les API de paiement"""
    
    @pytest.mark.django_db
    def test_initiate_payment_api(self, client, user, meter_reading):
        """Test API initiation paiement"""
        client.force_authenticate(user=user)
        
        response = client.post('/api/payment/initiate/', {
            'meter_reading_id': meter_reading.id,
            'amount': '150000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224612345678'
        })
        
        assert response.status_code == 201
        assert response.data['success'] is True
        assert 'transaction_reference' in response.data
    
    @pytest.mark.django_db
    def test_initiate_payment_missing_fields(self, client, user):
        """Test API avec champs manquants"""
        client.force_authenticate(user=user)
        
        response = client.post('/api/payment/initiate/', {
            'amount': '150000.00'
        })
        
        assert response.status_code == 400
        assert 'missing_fields' in response.data['error']
    
    @pytest.mark.django_db
    def test_payment_status_api(self, client, user, meter_reading):
        """Test API statut paiement"""
        payment = Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='COMPLETED',
            completed_at=timezone.now()
        )
        
        client.force_authenticate(user=user)
        response = client.get(f'/api/payment/status/{payment.transaction_reference}/')
        
        assert response.status_code == 200
        assert response.data['status'] == 'COMPLETED'
    
    @pytest.mark.django_db
    def test_list_receipts_api(self, client, user, meter_reading):
        """Test API liste reçus"""
        Payment.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='COMPLETED',
            completed_at=timezone.now(),
            receipt_generated=True
        )
        
        client.force_authenticate(user=user)
        response = client.get('/api/payment/receipts/')
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert len(response.data['receipts']) == 1
