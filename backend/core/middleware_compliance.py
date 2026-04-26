"""
Middleware de sécurité compliance pour Yobhou Fintech
Rate limiting, plafonds, et audit logging
"""

import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta

from apps.payments.models import Payment

logger = logging.getLogger('yobhou.security')


class ComplianceMiddleware:
    """
    Middleware de conformité BCEAO
    - Rate limiting par endpoint
    - Plafonds journaliers/mensuels
    - Audit logging
    """
    
    # Configuration plafonds (GNF)
    DAILY_LIMIT = 1_000_000  # 1M GNF
    MONTHLY_LIMIT = 5_000_000  # 5M GNF
    
    # Rate limits
    RATE_LIMITS = {
        'payment_initiate': {'count': 5, 'window': 3600},  # 5/heure
        'payment_confirm': {'count': 10, 'window': 3600},  # 10/heure
        'login': {'count': 5, 'window': 300},  # 5/5min
        'register': {'count': 3, 'window': 3600},  # 3/heure
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ne pas appliquer sur health check
        if request.path == '/api/health/':
            return self.get_response(request)
        
        # Vérifier rate limiting
        rate_limit_result = self._check_rate_limit(request)
        if rate_limit_result:
            self._log_security_event(request, 'RATE_LIMIT_EXCEEDED', rate_limit_result)
            return JsonResponse({
                'error': 'rate_limit_exceeded',
                'message': rate_limit_result['message'],
                'retry_after': rate_limit_result['retry_after']
            }, status=429)
        
        # Vérifier plafonds pour les paiements
        if request.path == '/api/payment/initiate/' and request.method == 'POST':
            limit_result = self._check_payment_limits(request)
            if limit_result:
                self._log_security_event(request, 'LIMIT_EXCEEDED', limit_result)
                return JsonResponse({
                    'error': limit_result['error'],
                    'message': limit_result['message']
                }, status=403)
        
        # Log audit
        self._log_request(request)
        
        response = self.get_response(request)
        
        # Log réponse
        self._log_response(request, response)
        
        return response
    
    def _check_rate_limit(self, request):
        """Vérifier rate limiting"""
        user = request.user if request.user.is_authenticated else None
        
        # Identifier l'endpoint
        endpoint = self._identify_endpoint(request)
        if not endpoint:
            return None
        
        limit_config = self.RATE_LIMITS.get(endpoint)
        if not limit_config:
            return None
        
        # Clé cache
        if user and user.is_authenticated:
            cache_key = f'rate_limit:{endpoint}:user:{user.id}'
        else:
            cache_key = f'rate_limit:{endpoint}:ip:{self._get_client_ip(request)}'
        
        # Incrémenter compteur
        count = cache.get(cache_key, 0) + 1
        cache.set(cache_key, count, limit_config['window'])
        
        if count > limit_config['count']:
            retry_after = cache.ttl(cache_key) if hasattr(cache, 'ttl') else limit_config['window']
            return {
                'message': f'Limite de {limit_config["count"]} requêtes par heure atteinte',
                'retry_after': retry_after
            }
        
        return None
    
    def _check_payment_limits(self, request):
        """Vérifier plafonds de paiement"""
        user = request.user if request.user.is_authenticated else None
        if not user:
            return None
        
        try:
            import json
            data = json.loads(request.body) if request.body else {}
            amount = float(data.get('amount', 0))
        except:
            return None
        
        # Vérifier plafond journalier
        today = timezone.now().date()
        daily_total = Payment.objects.filter(
            user=user,
            created_at__date=today,
            status__in=['INITIATED', 'CONFIRMED', 'COMPLETED']
        ).exclude(status='CANCELLED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        if daily_total + amount > self.DAILY_LIMIT:
            return {
                'error': 'daily_limit_exceeded',
                'message': f'Plafond journalier de {self.DAILY_LIMIT:,} GNF dépassé. Utilisé: {daily_total:,} GNF'
            }
        
        # Vérifier plafond mensuel
        month_start = today.replace(day=1)
        monthly_total = Payment.objects.filter(
            user=user,
            created_at__date__gte=month_start,
            status__in=['INITIATED', 'CONFIRMED', 'COMPLETED']
        ).exclude(status='CANCELLED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        if monthly_total + amount > self.MONTHLY_LIMIT:
            return {
                'error': 'monthly_limit_exceeded',
                'message': f'Plafond mensuel de {self.MONTHLY_LIMIT:,} GNF dépassé. Utilisé: {monthly_total:,} GNF'
            }
        
        return None
    
    def _identify_endpoint(self, request):
        """Identifier l'endpoint pour rate limiting"""
        path = request.path
        method = request.method
        
        if path == '/api/payment/initiate/' and method == 'POST':
            return 'payment_initiate'
        elif path == '/api/payment/confirm/' and method == 'POST':
            return 'payment_confirm'
        elif path == '/api/login/' and method == 'POST':
            return 'login'
        elif path == '/api/register/' and method == 'POST':
            return 'register'
        
        return None
    
    def _get_client_ip(self, request):
        """Récupérer IP client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def _log_request(self, request):
        """Log requête"""
        logger.info(
            'REQUEST',
            extra={
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'method': request.method,
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
                'timestamp': timezone.now().isoformat(),
            }
        )
    
    def _log_response(self, request, response):
        """Log réponse"""
        logger.info(
            'RESPONSE',
            extra={
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'status_code': response.status_code,
                'timestamp': timezone.now().isoformat(),
            }
        )
    
    def _log_security_event(self, request, event_type, details):
        """Log événement sécurité"""
        logger.warning(
            f'SECURITY_{event_type}',
            extra={
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'ip': self._get_client_ip(request),
                'details': str(details),
                'timestamp': timezone.now().isoformat(),
            }
        )


# Import nécessaire
from django.db import models
