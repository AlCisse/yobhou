"""
Rate Limiting Middleware - AML/Fintech Compliance
Prevents brute-force attacks on authentication and registration endpoints.
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import re


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting for sensitive endpoints:
    - /api/complete-registration/: 5 attempts/hour
    - /api/login/: 10 attempts/hour
    - /api/verify-otp/: 3 attempts/hour
    """

    RATE_LIMITS = {
        '/api/complete-registration/': {'requests': 10, 'window': 3600},  # 10/hour
        '/api/login/': {'requests': 10, 'window': 3600},  # 10/hour
        '/api/verify-otp/': {'requests': 5, 'window': 3600},  # 5/hour
        '/api/register/': {'requests': 10, 'window': 3600},  # 10/hour (increased for dev)
    }

    def process_request(self, request):
        path = request.path

        if path not in self.RATE_LIMITS:
            return None

        # Get client identifier (IP or phone number for registration)
        client_id = self._get_client_identifier(request, path)
        if not client_id:
            return None

        limit_config = self.RATE_LIMITS[path]
        cache_key = f"rate_limit:{path}:{client_id}"

        # Get current count
        current_count = cache.get(cache_key, 0)

        if current_count >= limit_config['requests']:
            # Rate limit exceeded
            return JsonResponse({
                'error': 'Trop de tentatives. Veuillez réessayer dans 1 heure.',
                'code': 'RATE_LIMIT_EXCEEDED'
            }, status=429)

        # Increment counter
        cache.set(cache_key, current_count + 1, limit_config['window'])

        return None

    def _get_client_identifier(self, request, path):
        """Extract client identifier for rate limiting"""
        # For registration endpoints, use phone number if available
        if 'registration' in path or 'register' in path:
            phone = request.data.get('phone_number') if hasattr(request, 'data') else None
            if phone:
                # Validate phone format strictly
                if re.match(r'^\+224\d{9}$', phone):
                    return f"phone:{phone}"

        # Fallback to IP
        ip = self._get_client_ip(request)
        return f"ip:{ip}" if ip else None

    def _get_client_ip(self, request):
        """Get client IP address, handling proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
