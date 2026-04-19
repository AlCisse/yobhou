import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from apps.transactions.models import Transaction
from apps.meters.models import MeterReading
from apps.transactions.services.aml_checker import AMLChecker, check_transaction_aml

User = get_user_model()


@pytest.mark.django_db
class TestTransactionModel:
    def test_create_transaction(self):
        user = User.objects.create_user(
            username='testuser',
            phone_number='+224601234567',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='12345678',
            previous_index=400.0,
            current_index=450.0,
            consumption=50.0,
            ocr_data={}
        )
        
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('125000.00'),
            payment_method='orange_money',
            reference_number='YBH-TEST-001'
        )
        
        assert transaction.amount == Decimal('125000.00')
        assert transaction.status == 'pending'
        assert transaction.payment_method == 'orange_money'
        assert transaction.aml_alerts == []
    
    def test_transaction_str(self):
        user = User.objects.create_user(
            username='testuser2',
            phone_number='+224601234568',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='87654321',
            previous_index=300.0,
            current_index=500.0,
            consumption=200.0,
            ocr_data={}
        )
        
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('200000.00'),
            payment_method='mtn_momo',
            reference_number='YBH-TEST-002'
        )
        
        assert 'YBH-TEST-002' in str(transaction)


@pytest.mark.django_db
class TestAMLChecker:
    def test_clean_transaction(self):
        user = User.objects.create_user(
            username='cleanuser',
            phone_number='+224601234569',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='11111111',
            previous_index=100.0,
            current_index=150.0,
            consumption=50.0,
            ocr_data={}
        )
        
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('50000.00'),  # Normal amount
            payment_method='orange_money',
            reference_number='YBH-CLEAN-001'
        )
        
        alerts = check_transaction_aml(transaction)
        assert len(alerts) == 0
        assert transaction.status == 'pending'
    
    def test_structuring_detection(self):
        user = User.objects.create_user(
            username='structuser',
            phone_number='+224601234570',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='22222222',
            previous_index=200.0,
            current_index=250.0,
            consumption=50.0,
            ocr_data={}
        )
        
        # Create 2 transactions just below threshold (950k GNF)
        one_hour_ago = datetime.utcnow() - timedelta(minutes=30)
        
        Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('950000.00'),
            payment_method='orange_money',
            reference_number='YBH-STRUCT-001',
            status='completed',
            created_at=one_hour_ago
        )
        
        Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('940000.00'),
            payment_method='mtn_momo',
            reference_number='YBH-STRUCT-002',
            status='completed',
            created_at=one_hour_ago + timedelta(minutes=15)
        )
        
        # Third transaction - should trigger structuring alert
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('960000.00'),
            payment_method='orange_money',
            reference_number='YBH-STRUCT-003',
            status='completed'
        )
        
        alerts = check_transaction_aml(transaction)
        structuring_alerts = [a for a in alerts if a['type'] == 'STRUCTURING']
        assert len(structuring_alerts) > 0
        assert structuring_alerts[0]['severity'] == 'HIGH'
    
    def test_daily_limit_exceeded(self):
        user = User.objects.create_user(
            username='limituser',
            phone_number='+224601234571',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='33333333',
            previous_index=300.0,
            current_index=350.0,
            consumption=50.0,
            ocr_data={}
        )
        
        # Create transactions exceeding daily limit (1M GNF)
        Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('600000.00'),
            payment_method='orange_money',
            reference_number='YBH-LIMIT-001',
            status='completed'
        )
        
        transaction2 = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('500000.00'),
            payment_method='orange_money',
            reference_number='YBH-LIMIT-002',
            status='completed'
        )
        
        alerts = check_transaction_aml(transaction2)
        limit_alerts = [a for a in alerts if a['type'] == 'DAILY_LIMIT_EXCEEDED']
        assert len(limit_alerts) > 0
        assert limit_alerts[0]['severity'] == 'CRITICAL'
    
    def test_rapid_succession(self):
        user = User.objects.create_user(
            username='rapiduser',
            phone_number='+224601234572',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='44444444',
            previous_index=400.0,
            current_index=450.0,
            consumption=50.0,
            ocr_data={}
        )
        
        # Create 4 transactions in last hour
        for i in range(4):
            Transaction.objects.create(
                user=user,
                meter_reading=meter_reading,
                amount=Decimal('50000.00'),
                payment_method='orange_money',
                reference_number=f'YBH-RAPID-{i:03d}',
                status='completed'
            )
        
        # 5th transaction should trigger alert
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('50000.00'),
            payment_method='orange_money',
            reference_number='YBH-RAPID-004',
            status='completed'
        )
        
        alerts = check_transaction_aml(transaction)
        rapid_alerts = [a for a in alerts if a['type'] == 'RAPID_SUCCESSION']
        assert len(rapid_alerts) > 0
        assert rapid_alerts[0]['severity'] == 'MEDIUM'
    
    def test_flagged_transaction_auto_status(self):
        user = User.objects.create_user(
            username='flaguser',
            phone_number='+224601234573',
            password='testpass123'
        )
        
        meter_reading = MeterReading.objects.create(
            user=user,
            meter_number='55555555',
            previous_index=500.0,
            current_index=550.0,
            consumption=50.0,
            ocr_data={}
        )
        
        # Transaction exceeding daily limit should auto-flag
        Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('600000.00'),
            payment_method='orange_money',
            reference_number='YBH-FLAG-001',
            status='completed'
        )
        
        transaction = Transaction.objects.create(
            user=user,
            meter_reading=meter_reading,
            amount=Decimal('600000.00'),
            payment_method='orange_money',
            reference_number='YBH-FLAG-002',
            status='completed'
        )
        
        # Should be auto-flagged due to CRITICAL alert
        assert transaction.status == 'flagged'
        assert len(transaction.aml_alerts) > 0
