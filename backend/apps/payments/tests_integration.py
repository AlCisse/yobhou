"""
Tests d'intégration pour le flux complet de paiement
Scénario : Scan facture → Paiement → Reçu
"""

import pytest
import os
import tempfile
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from apps.payments.models import Payment
from apps.meters.models import MeterReading
from apps.users.models import User


User = get_user_model()


class PaymentIntegrationTests(TestCase):
    """Tests d'intégration du flux de paiement"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.client = Client()
        
        # Créer utilisateur test
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+224612345678',
            password='testpass123',
            date_of_birth='1990-01-01'
        )
        
        # Créer relevé compteur
        self.meter = MeterReading.objects.create(
            user=self.user,
            meter_number='12345678',
            previous_index=1100.0,
            current_index=1250.5,
            consumption=150.5,
            ocr_data={'confidence': 0.99, 'meter_number': '12345678'},
            is_validated=True
        )
        
        # Login
        response = self.client.post('/api/login/', {
            'phone_number': '+224612345678',
            'password': 'testpass123'
        }, content_type='application/json')
        
        self.token = response.json()['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
    
    @patch('apps.payments.services.mobile_money.MobileMoneyService.initiate_payment')
    def test_complete_payment_flow(self, mock_initiate):
        """Test flux complet : Initiate → Confirm → Receipt"""
        # Mock initiation
        mock_initiate.return_value = {
            'success': True,
            'operator_reference': 'OM-TEST-12345',
            'status': 'PENDING',
            'message': 'Paiement initié'
        }
        
        # Étape 1 : Initier paiement
        response = self.client.post('/api/payment/initiate/', {
            'meter_reading_id': self.meter.id,
            'amount': '150000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224612345678'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('transaction_reference', data)
        self.assertEqual(data['status'], 'INITIATED')
        
        payment_id = data['payment_id']
        reference = data['transaction_reference']
        
        # Étape 2 : Vérifier statut
        response = self.client.get(f'/api/payment/status/{reference}/')
        self.assertEqual(response.status_code, 200)
        status_data = response.json()
        self.assertEqual(status_data['status'], 'INITIATED')
        
        # Étape 3 : Confirmer paiement
        with patch('apps.payments.services.mobile_money.MobileMoneyService.verify_payment') as mock_verify:
            mock_verify.return_value = {
                'success': True,
                'status': 'SUCCESS',
                'message': 'Paiement confirmé'
            }
            
            response = self.client.post('/api/payment/confirm/', {
                'payment_id': payment_id
            }, content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            confirm_data = response.json()
            self.assertTrue(confirm_data['success'])
            self.assertEqual(confirm_data['status'], 'COMPLETED')
        
        # Étape 4 : Vérifier liste reçus
        response = self.client.get('/api/payment/receipts/')
        self.assertEqual(response.status_code, 200)
        receipts = response.json()
        self.assertEqual(receipts['count'], 1)
    
    def test_payment_without_authentication(self):
        """Test paiement sans authentification"""
        client = Client()  # Sans auth
        
        response = client.post('/api/payment/initiate/', {
            'meter_reading_id': self.meter.id,
            'amount': '150000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224612345678'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_payment_exceeds_daily_limit(self):
        """Test dépassement plafond journalier"""
        # Créer 3 paiements pour atteindre le plafond
        for i in range(3):
            Payment.objects.create(
                user=self.user,
                meter_reading=self.meter,
                amount=Decimal('400000.00'),
                payment_method='ORANGE_MONEY',
                payment_phone='+224612345678',
                status='COMPLETED',
                transaction_reference=f'YBH-LIMIT-{i}',
                completed_at=timezone.now()
            )
        
        # Tenter un 4ème paiement
        response = self.client.post('/api/payment/initiate/', {
            'meter_reading_id': self.meter.id,
            'amount': '150000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224612345678'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('limit_exceeded', data['error'])
    
    def test_payment_invalid_meter(self):
        """Test paiement avec compteur invalide"""
        response = self.client.post('/api/payment/initiate/', {
            'meter_reading_id': 99999,  # ID inexistant
            'amount': '150000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224612345678'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
    
    def test_payment_missing_fields(self):
        """Test paiement avec champs manquants"""
        response = self.client.post('/api/payment/initiate/', {
            'amount': '150000.00'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error'], 'missing_fields')
    
    def test_rate_limiting(self):
        """Test rate limiting (5 paiements/heure)"""
        with patch('apps.payments.services.mobile_money.MobileMoneyService.initiate_payment') as mock_init:
            mock_init.return_value = {
                'success': True,
                'operator_reference': 'OM-TEST',
                'status': 'PENDING'
            }
            
            # Créer 5 paiements
            for i in range(5):
                Payment.objects.create(
                    user=self.user,
                    meter_reading=self.meter,
                    amount=Decimal('1000.00'),
                    payment_method='ORANGE_MONEY',
                    payment_phone='+224612345678',
                    status='INITIATED',
                    transaction_reference=f'YBH-RATE-{i}',
                    created_at=timezone.now()
                )
            
            # 6ème tentative doit échouer
            response = self.client.post('/api/payment/initiate/', {
                'meter_reading_id': self.meter.id,
                'amount': '1000.00',
                'payment_method': 'ORANGE_MONEY',
                'payment_phone': '+224612345678'
            }, content_type='application/json')
            
            self.assertEqual(response.status_code, 429)
    
    def test_receipt_generation(self):
        """Test génération reçu PDF"""
        # Créer paiement complété
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='COMPLETED',
            transaction_reference='YBH-REC-001',
            completed_at=timezone.now(),
            receipt_generated=True
        )
        
        # Télécharger reçu
        response = self.client.get(f'/api/payment/receipts/{payment.id}/pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_payment_timeout(self):
        """Test expiration paiement (15 minutes)"""
        # Créer paiement initié il y a 20 minutes
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('150000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345678',
            status='INITIATED',
            transaction_reference='YBH-TIMEOUT-001',
            initiated_at=timezone.now() - timedelta(minutes=20)
        )
        
        # Tenter confirmation
        response = self.client.post('/api/payment/confirm/', {
            'payment_id': payment.id
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 408)
        data = response.json()
        self.assertEqual(data['error'], 'timeout')


class PaymentModelTests(TestCase):
    """Tests modèle Payment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='modeluser',
            phone_number='+224612345679',
            password='testpass'
        )
        self.meter = MeterReading.objects.create(
            user=self.user,
            meter_number='87654321',
            current_index=2000.0
        )
    
    def test_transaction_reference_generation(self):
        """Test génération référence unique"""
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('100000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345679'
        )
        
        self.assertTrue(payment.transaction_reference.startswith('YBH-'))
        self.assertEqual(len(payment.transaction_reference), 16)  # YBH- + 12 chars
    
    def test_status_default(self):
        """Test statut par défaut"""
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('100000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345679'
        )
        
        self.assertEqual(payment.status, 'PENDING')
    
    def test_amount_precision(self):
        """Test précision montant"""
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('150000.50'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345679'
        )
        
        self.assertEqual(payment.amount, Decimal('150000.50'))
    
    def test_payment_str(self):
        """Test représentation string"""
        payment = Payment.objects.create(
            user=self.user,
            meter_reading=self.meter,
            amount=Decimal('100000.00'),
            payment_method='ORANGE_MONEY',
            payment_phone='+224612345679'
        )
        
        expected = f'Payment {payment.transaction_reference} - PENDING'
        self.assertEqual(str(payment), expected)
