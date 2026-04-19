from django.db import models
from apps.users.models import User
from apps.meters.models import MeterReading
from .services import check_transaction_aml
import logging

logger = logging.getLogger('yobhou.audit')


class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('flagged', 'Flagged - AML Review'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meter_reading = models.ForeignKey(MeterReading, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # e.g., 'orange_money', 'mtn_momo', 'agency'
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=100, unique=True)
    aml_alerts = models.JSONField(default=list, blank=True)  # Store AML check results
    aml_reviewed = models.BooleanField(default=False)  # True if manually reviewed
    aml_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='aml_reviewer')
    aml_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.reference_number} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Run AML check on transaction creation or status change to completed
        is_new = self._state.adding
        status_changed_to_completed = (
            not is_new and 
            self.status == 'completed' and 
            Transaction.objects.filter(pk=self.pk).values_list('status', flat=True).first() != 'completed'
        )
        
        if is_new or status_changed_to_completed:
            logger.info(f"Running AML check for transaction {self.reference_number}")
            alerts = check_transaction_aml(self)
            
            if alerts:
                self.aml_alerts = alerts
                # Auto-flag if any HIGH or CRITICAL alert
                if any(a['severity'] in ['HIGH', 'CRITICAL'] for a in alerts):
                    self.status = 'flagged'
                    logger.warning(f"Transaction {self.reference_number} flagged for AML review")
            
            super().save(*args, **kwargs)
            
            # Log AML result
            if alerts:
                logger.warning(f"AML alerts for {self.reference_number}: {alerts}")
            else:
                logger.info(f"AML check passed for {self.reference_number}")
        else:
            super().save(*args, **kwargs)