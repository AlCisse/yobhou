"""
Tests End-to-End Yobhou
Scénario complet : Inscription → Scan → Paiement → Reçu
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
import json

from apps.users.models import User
from apps.meters.models import MeterReading
from apps.payments.models import Payment


class E2EUserJourney(TestCase):
    """Test parcours utilisateur complet"""
    
    def setUp(self):
        self.client = Client()
    
    def test_user_journey_complete(self):
        """Test E2E : Inscription → Upload → Paiement → Reçu"""
        
        # ÉTAPE 1 : Inscription
        print("\n=== ÉTAPE 1: Inscription ===")
        response = self.client.post('/api/register/', {
            'phone_number': '+224600000001',
            'date_of_birth': '1990-01-01',
            'password': 'SecurePass123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        register_data = response.json()
        print(f"✅ Inscription réussie: {register_data['user_id']}")
        
        # ÉTAPE 2 : Login
        print("\n=== ÉTAPE 2: Login ===")
        response = self.client.post('/api/login/', {
            'phone_number': '+224600000001',
            'password': 'SecurePass123!'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        login_data = response.json()
        token = login_data['access']
        print(f"✅ Login réussi, token obtenu")
        
        # Configurer auth
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        # ÉTAPE 3 : Upload facture (simulé)
        print("\n=== ÉTAPE 3: Upload Facture ===")
        # Note: Upload multipart difficile à tester sans image
        # On crée directement le MeterReading
        user = User.objects.get(phone_number='+224600000001')
        meter = MeterReading.objects.create(
            user=user,
            meter_number='TEST123456',
            previous_index=1000.0,
            current_index=1200.0,
            consumption=200.0,
            is_validated=True
        )
        print(f"✅ Facture uploadée (simulé), compteur: {meter.meter_number}")
        
        # ÉTAPE 4 : Initier paiement
        print("\n=== ÉTAPE 4: Initier Paiement ===")
        with pytest.mock.patch('apps.payments.services.mobile_money.MobileMoneyService.initiate_payment') as mock:
            mock.return_value = {
                'success': True,
                'operator_reference': 'OM-E2E-123',
                'status': 'PENDING'
            }
            
            response = self.client.post('/api/payment/initiate/', {
                'meter_reading_id': meter.id,
                'amount': '50000.00',
                'payment_method': 'ORANGE_MONEY',
                'payment_phone': '+224600000001'
            }, content_type='application/json')
            
            self.assertEqual(response.status_code, 201)
            payment_data = response.json()
            payment_id = payment_data['payment_id']
            reference = payment_data['transaction_reference']
            print(f"✅ Paiement initié: {reference}")
        
        # ÉTAPE 5 : Confirmer paiement
        print("\n=== ÉTAPE 5: Confirmer Paiement ===")
        with pytest.mock.patch('apps.payments.services.mobile_money.MobileMoneyService.verify_payment') as mock:
            mock.return_value = {
                'success': True,
                'status': 'SUCCESS'
            }
            
            response = self.client.post('/api/payment/confirm/', {
                'payment_id': payment_id
            }, content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            print(f"✅ Paiement confirmé")
        
        # ÉTAPE 6 : Vérifier reçu
        print("\n=== ÉTAPE 6: Vérifier Reçu ===")
        response = self.client.get('/api/payment/receipts/')
        self.assertEqual(response.status_code, 200)
        receipts = response.json()
        self.assertEqual(receipts['count'], 1)
        print(f"✅ Reçu disponible: {receipts['receipts'][0]['transaction_reference']}")
        
        # ÉTAPE 7 : Télécharger PDF
        print("\n=== ÉTAPE 7: Télécharger PDF ===")
        payment = Payment.objects.get(id=payment_id)
        payment.receipt_generated = True
        payment.save()
        
        response = self.client.get(f'/api/payment/receipts/{payment_id}/pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        print(f"✅ PDF reçu téléchargé ({len(response.content)} bytes)")
        
        print("\n" + "="*50)
        print("✅ PARCOURS E2E COMPLET RÉUSSI")
        print("="*50)
    
    def test_e2e_payment_limits(self):
        """Test E2E : Plafonds BCEAO"""
        # Créer utilisateur
        user = User.objects.create_user(
            username='limituser',
            phone_number='+224600000002',
            password='testpass',
            date_of_birth='1990-01-01'
        )
        
        # Login
        response = self.client.post('/api/login/', {
            'phone_number': '+224600000002',
            'password': 'testpass'
        }, content_type='application/json')
        token = response.json()['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        # Créer compteur
        meter = MeterReading.objects.create(
            user=user,
            meter_number='LIMIT001',
            current_index=1000.0
        )
        
        # Créer paiements pour atteindre le plafond (1M GNF)
        for i in range(2):
            Payment.objects.create(
                user=user,
                meter_reading=meter,
                amount=Decimal('500000.00'),
                payment_method='ORANGE_MONEY',
                payment_phone='+224600000002',
                status='COMPLETED',
                transaction_reference=f'LIMIT-{i}',
                completed_at=timezone.now()
            )
        
        # Tenter un 3ème paiement de 500k (dépasserait le plafond)
        response = self.client.post('/api/payment/initiate/', {
            'meter_reading_id': meter.id,
            'amount': '500000.00',
            'payment_method': 'ORANGE_MONEY',
            'payment_phone': '+224600000002'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        print("✅ Plafond journalier respecté (1M GNF)")
    
    def test_e2e_invalid_credentials(self):
        """Test E2E : Authentification invalide"""
        # Tentative avec token invalide
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer INVALID_TOKEN'
        
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
        print("✅ Authentification invalide rejetée")
