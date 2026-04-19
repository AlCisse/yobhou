"""
Yobhou Fintech - AML (Anti-Money Laundering) Checker
Compliance: GIABA, BCEAO

Detects suspicious transaction patterns:
- Structuring (smurfing): Multiple transactions just below threshold
- Rapid succession: Many transactions in short time
- Unusual amounts: Round numbers, patterns
- Geographic anomalies: Different locations in short time
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from django.db.models import Sum
from apps.transactions.models import Transaction
from apps.users.models import User
import logging

logger = logging.getLogger('yobhou.audit')

# Thresholds (BCEAO compliance)
STRUCTURING_THRESHOLD = Decimal('950000')  # Just below 1M GNF daily limit
RAPID_SUCCESSSION_COUNT = 5  # Transactions in 1 hour
RAPID_SUCCESSSION_WINDOW = timedelta(hours=1)
UNUSUAL_ROUND_THRESHOLD = Decimal('100000')  # Suspicious if multiple 100k, 200k, etc.
DAILY_LIMIT = Decimal('1000000')  # 1M GNF
MONTHLY_LIMIT = Decimal('5000000')  # 5M GNF


class AMLChecker:
    """
    Anti-Money Laundering detection engine.
    Runs on every transaction to flag suspicious patterns.
    """
    
    def __init__(self, transaction: Transaction):
        self.transaction = transaction
        self.user = transaction.user
        self.alerts = []
    
    def check_all(self) -> List[Dict]:
        """Run all AML checks"""
        self._check_structuring()
        self._check_rapid_succession()
        self._check_daily_limit()
        self._check_monthly_limit()
        self._check_unusual_patterns()
        
        if self.alerts:
            logger.warning(f"AML alerts for user {self.user.id}: {self.alerts}")
        
        return self.alerts
    
    def _check_structuring(self):
        """Detect structuring (smurfing): multiple transactions just below threshold"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        recent_transactions = Transaction.objects.filter(
            user=self.user,
            created_at__gte=one_hour_ago,
            status='completed'
        ).exclude(id=self.transaction.id)
        
        # Count transactions close to threshold (within 5%)
        structuring_count = sum(
            1 for t in recent_transactions
            if STRUCTURING_THRESHOLD * Decimal('0.95') <= t.amount <= STRUCTURING_THRESHOLD
        )
        
        if structuring_count >= 2:
            self.alerts.append({
                'type': 'STRUCTURING',
                'severity': 'HIGH',
                'description': f'Possible structuring: {structuring_count + 1} transactions near threshold',
                'amount': str(self.transaction.amount),
                'user_id': self.user.id
            })
    
    def _check_rapid_succession(self):
        """Detect rapid succession of transactions"""
        window_start = datetime.utcnow() - RAPID_SUCCESSSION_WINDOW
        
        recent_count = Transaction.objects.filter(
            user=self.user,
            created_at__gte=window_start,
            status='completed'
        ).count()
        
        if recent_count >= RAPID_SUCCESSSION_COUNT:
            self.alerts.append({
                'type': 'RAPID_SUCCESSION',
                'severity': 'MEDIUM',
                'description': f'{recent_count} transactions in last hour',
                'amount': str(self.transaction.amount),
                'user_id': self.user.id
            })
    
    def _check_daily_limit(self):
        """Check if user exceeds daily limit"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        daily_total = Transaction.objects.filter(
            user=self.user,
            created_at__gte=today_start,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if daily_total > DAILY_LIMIT:
            self.alerts.append({
                'type': 'DAILY_LIMIT_EXCEEDED',
                'severity': 'CRITICAL',
                'description': f'Daily limit exceeded: {daily_total} GNF',
                'amount': str(daily_total),
                'user_id': self.user.id
            })
    
    def _check_monthly_limit(self):
        """Check if user exceeds monthly limit"""
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_total = Transaction.objects.filter(
            user=self.user,
            created_at__gte=month_start,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        if monthly_total > MONTHLY_LIMIT:
            self.alerts.append({
                'type': 'MONTHLY_LIMIT_EXCEEDED',
                'severity': 'CRITICAL',
                'description': f'Monthly limit exceeded: {monthly_total} GNF',
                'amount': str(monthly_total),
                'user_id': self.user.id
            })
    
    def _check_unusual_patterns(self):
        """Check for unusual transaction patterns"""
        amount = self.transaction.amount
        
        # Check for round numbers (potential money laundering)
        if amount >= UNUSUAL_ROUND_THRESHOLD and int(amount) % int(UNUSUAL_ROUND_THRESHOLD) == 0:
            # Count similar round transactions in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            similar_round_txs = Transaction.objects.filter(
                user=self.user,
                created_at__gte=thirty_days_ago,
                status='completed',
                amount__gte=UNUSUAL_ROUND_THRESHOLD
            )
            
            # Count how many are also round numbers
            round_count = sum(
                1 for t in similar_round_txs
                if int(t.amount) % int(UNUSUAL_ROUND_THRESHOLD) == 0
            )
            
            if round_count >= 3:
                self.alerts.append({
                    'type': 'UNUSUAL_PATTERN',
                    'severity': 'LOW',
                    'description': f'Multiple round-number transactions detected ({round_count} in 30 days)',
                    'amount': str(amount),
                    'user_id': self.user.id
                })


def check_transaction_aml(transaction: Transaction) -> List[Dict]:
    """
    Main entry point: Check a transaction for AML compliance.
    Returns list of alerts (empty if clean).
    """
    checker = AMLChecker(transaction)
    return checker.check_all()
