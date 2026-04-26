from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Payment(models.Model):
    """Modèle de paiement pour factures EDG"""
    
    PAYMENT_METHOD_CHOICES = [
        ('ORANGE_MONEY', 'Orange Money'),
        ('MTN_MOMO', 'MTN MoMo'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('INITIATED', 'Initié'),
        ('CONFIRMED', 'Confirmé'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échoué'),
        ('CANCELLED', 'Annulé'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    meter_reading = models.ForeignKey(
        'meters.MeterReading',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    
    # Montant
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Montant en GNF'
    )
    
    # Méthode de paiement
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Références
    transaction_reference = models.CharField(
        max_length=50,
        unique=True,
        help_text='Référence unique Yobhou'
    )
    
    operator_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Référence opérateur Mobile Money'
    )
    
    # Téléphone utilisé pour paiement
    payment_phone = models.CharField(
        max_length=20,
        help_text='Numéro téléphone utilisé pour paiement'
    )
    
    # Reçu
    receipt_generated = models.BooleanField(default=False)
    receipt_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    initiated_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Raison échec
    failure_reason = models.TextField(blank=True)
    
    # Audit
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'Payment {self.transaction_reference} - {self.status}'
    
    def save(self, *args, **kwargs):
        if not self.transaction_reference:
            self.transaction_reference = f'YBH-{uuid.uuid4().hex[:12].upper()}'
        super().save(*args, **kwargs)
