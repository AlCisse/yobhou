"""
Yobhou Fintech - Logging Filters for Audit Compliance
Adds user context to all log records for traceability (10-year audit)
"""

import logging
from threading import local

# Thread-local storage for user context
_user_context = local()


class UserContextFilter(logging.Filter):
    """
    Filter that adds user context to log records.
    Used for audit trail compliance (BCEAO, 10-year retention).
    """
    
    def filter(self, record):
        try:
            # Get user context from thread-local storage
            user_id = getattr(_user_context, 'user_id', 'anonymous')
            user_ip = getattr(_user_context, 'user_ip', 'unknown')
            session_id = getattr(_user_context, 'session_id', 'unknown')
            action = getattr(_user_context, 'action', 'unknown')
            
            # Add to log record
            record.user_id = user_id
            record.user_ip = user_ip
            record.session_id = session_id
            record.action = action
            
            return True
        except Exception:
            # Fallback for context-less logs
            record.user_id = 'system'
            record.user_ip = 'localhost'
            record.session_id = 'none'
            record.action = 'system_event'
            return True


def set_user_context(user_id=None, user_ip=None, session_id=None, action=None):
    """
    Set user context for current thread.
    Call this at the beginning of each request.
    """
    _user_context.user_id = user_id
    _user_context.user_ip = user_ip
    _user_context.session_id = session_id
    _user_context.action = action


def clear_user_context():
    """Clear user context at end of request"""
    if hasattr(_user_context, 'user_id'):
        delattr(_user_context, 'user_id')
    if hasattr(_user_context, 'user_ip'):
        delattr(_user_context, 'user_ip')
    if hasattr(_user_context, 'session_id'):
        delattr(_user_context, 'session_id')
    if hasattr(_user_context, 'action'):
        delattr(_user_context, 'action')


class AuditMiddleware:
    """
    Django middleware to set user context for each request.
    Ensures all logs have proper audit trail.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract user context from request
        user_id = getattr(request.user, 'id', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        user_ip = self.get_client_ip(request)
        session_id = request.session.session_key if hasattr(request, 'session') else 'unknown'
        
        # Set context
        set_user_context(
            user_id=user_id,
            user_ip=user_ip,
            session_id=session_id,
            action=f"{request.method} {request.path}"
        )
        
        # Log request start
        logger = logging.getLogger('yobhou.audit')
        logger.info(f"Request started: {request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log request end
        logger.info(f"Request completed: {request.method} {request.path} status={response.status_code}")
        
        # Clear context
        clear_user_context()
        
        return response
    
    def get_client_ip(self, request):
        """Extract client IP from request headers"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
