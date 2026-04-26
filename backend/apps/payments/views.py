from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime, timedelta

from apps.payments.models import Payment
from apps.meters.models import MeterReading
from apps.payments.services.mobile_money import MobileMoneyService
from apps.payments.services.receipt_generator import ReceiptGenerator
from apps.transactions.services.aml_checker import AMLChecker
from core.utils import get_client_ip


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initier un paiement de facture EDG
    
    Expected JSON:
    {
        "meter_reading_id": 123,
        "amount": 150000.00,
        "payment_method": "ORANGE_MONEY",
        "payment_phone": "+224612345678"
    }
    """
    user = request.user
    data = request.data
    
    try:
        # Validation données
        meter_reading_id = data.get('meter_reading_id')
        amount = float(data.get('amount', 0))
        payment_method = data.get('payment_method')
        payment_phone = data.get('payment_phone')
        
        if not all([meter_reading_id, amount, payment_method, payment_phone]):
            return Response({
                'error': 'missing_fields',
                'message': 'Tous les champs sont obligatoires'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que le meter reading existe et appartient à l'utilisateur
        meter_reading = get_object_or_404(
            MeterReading, 
            id=meter_reading_id, 
            user=user
        )
        
        # Vérifier plafonds
        aml_checker = AMLChecker(user)
        limit_check = aml_checker.check_daily_limit(amount)
        if limit_check['limit_exceeded']:
            return Response({
                'error': 'daily_limit_exceeded',
                'message': f"Plafond journalier dépassé. Limite: {limit_check['limit']:,} GNF"
            }, status=status.HTTP_403_FORBIDDEN)
        
        monthly_check = aml_checker.check_monthly_limit(amount)
        if monthly_check['limit_exceeded']:
            return Response({
                'error': 'monthly_limit_exceeded',
                'message': f"Plafond mensuel dépassé. Limite: {monthly_check['limit']:,} GNF"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Rate limiting
        recent_payments = Payment.objects.filter(
            user=user,
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).count()
        
        if recent_payments >= 5:
            return Response({
                'error': 'rate_limit_exceeded',
                'message': 'Limite de 5 paiements par heure atteinte'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Créer le paiement
        with transaction.atomic():
            payment = Payment.objects.create(
                user=user,
                meter_reading=meter_reading,
                amount=amount,
                payment_method=payment_method,
                payment_phone=payment_phone,
                status='PENDING',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Initier paiement Mobile Money
            mobile_money = MobileMoneyService()
            result = mobile_money.initiate_payment(
                phone=payment_phone,
                amount=amount,
                reference=payment.transaction_reference,
                payment_method=payment_method
            )
            
            if result['success']:
                payment.status = 'INITIATED'
                payment.operator_reference = result['operator_reference']
                payment.initiated_at = datetime.now()
                payment.save()
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_reference': payment.transaction_reference,
                    'status': payment.status,
                    'message': result['message'],
                    'next_step': 'confirm_payment',
                    'timeout_minutes': 15
                }, status=status.HTTP_201_CREATED)
            else:
                payment.status = 'FAILED'
                payment.failure_reason = result.get('message', 'Échec initiation')
                payment.failed_at = datetime.now()
                payment.save()
                
                return Response({
                    'error': 'initiation_failed',
                    'message': result.get('message', 'Échec de l\'initiation')
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'error': 'server_error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """
    Confirmer un paiement (après validation utilisateur sur téléphone)
    
    Expected JSON:
    {
        "payment_id": 123,
        "otp_code": "123456"  # Optional
    }
    """
    user = request.user
    data = request.data
    
    try:
        payment_id = data.get('payment_id')
        
        if not payment_id:
            return Response({
                'error': 'missing_payment_id',
                'message': 'ID de paiement requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment = get_object_or_404(
            Payment,
            id=payment_id,
            user=user,
            status='INITIATED'
        )
        
        # Vérifier expiration (15 minutes)
        if payment.initiated_at and \
           datetime.now() > payment.initiated_at + timedelta(minutes=15):
            payment.status = 'FAILED'
            payment.failure_reason = 'Délai de confirmation dépassé'
            payment.failed_at = datetime.now()
            payment.save()
            
            return Response({
                'error': 'timeout',
                'message': 'Le délai de 15 minutes est dépassé. Veuillez réessayer.'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        # Vérifier paiement avec opérateur
        mobile_money = MobileMoneyService()
        result = mobile_money.verify_payment(
            operator_reference=payment.operator_reference,
            payment_method=payment.payment_method
        )
        
        if result['status'] == 'SUCCESS':
            payment.status = 'COMPLETED'
            payment.completed_at = datetime.now()
            payment.save()
            
            # Générer reçu
            try:
                receipt_pdf = ReceiptGenerator.generate_pdf(payment)
                # TODO: Sauvegarder sur S3 et mettre à jour receipt_url
                payment.receipt_generated = True
                payment.save()
            except Exception as e:
                # Log erreur mais ne pas bloquer
                print(f"Erreur génération reçu: {e}")
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'transaction_reference': payment.transaction_reference,
                'status': payment.status,
                'message': 'Paiement confirmé avec succès',
                'receipt_ready': payment.receipt_generated,
                'next_step': 'view_receipt'
            }, status=status.HTTP_200_OK)
        else:
            payment.status = 'CONFIRMED'
            payment.confirmed_at = datetime.now()
            payment.save()
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'status': payment.status,
                'message': 'Paiement en cours de traitement',
                'next_step': 'wait_confirmation'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'server_error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, reference):
    """
    Vérifier le statut d'un paiement
    """
    try:
        payment = get_object_or_404(
            Payment,
            transaction_reference=reference,
            user=request.user
        )
        
        return Response({
            'payment_id': payment.id,
            'transaction_reference': payment.transaction_reference,
            'status': payment.status,
            'amount': float(payment.amount),
            'payment_method': payment.get_payment_method_display(),
            'created_at': payment.created_at.isoformat(),
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
            'receipt_ready': payment.receipt_generated
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'server_error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_receipts(request):
    """
    Liste des reçus de l'utilisateur
    """
    try:
        payments = Payment.objects.filter(
            user=request.user,
            status='COMPLETED',
            receipt_generated=True
        ).order_by('-created_at')
        
        receipts = []
        for payment in payments:
            receipts.append({
                'payment_id': payment.id,
                'transaction_reference': payment.transaction_reference,
                'amount': float(payment.amount),
                'date': payment.completed_at.isoformat() if payment.completed_at else payment.created_at.isoformat(),
                'meter_number': payment.meter_reading.meter_number if payment.meter_reading else None,
                'download_url': payment.receipt_url if payment.receipt_url else None
            })
        
        return Response({
            'count': len(receipts),
            'receipts': receipts
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'server_error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_receipt(request, payment_id):
    """
    Télécharger le reçu PDF d'un paiement
    """
    try:
        payment = get_object_or_404(
            Payment,
            id=payment_id,
            user=request.user,
            status='COMPLETED'
        )
        
        # TODO: Récupérer depuis S3 ou générer à la volée
        receipt_pdf = ReceiptGenerator.generate_pdf(payment)
        
        from django.http import HttpResponse
        response = HttpResponse(receipt_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reçu_{payment.transaction_reference}.pdf"'
        
        return response
        
    except Exception as e:
        return Response({
            'error': 'server_error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
