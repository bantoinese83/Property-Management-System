from django.utils.deprecation import MiddlewareMixin
from .signals import set_audit_context


class AuditMiddleware(MiddlewareMixin):
    """Middleware to capture request context for audit logging"""

    def process_request(self, request):
        """Set audit context at the start of each request"""
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            set_audit_context(user=user, request=request)
        else:
            set_audit_context(request=request)

    def process_exception(self, request, exception):
        """Log exceptions for audit purposes"""
        # Could add exception logging here if needed
        pass

    def process_response(self, request, response):
        """Clean up audit context after request"""
        set_audit_context()
        return response