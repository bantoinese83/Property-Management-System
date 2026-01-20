"""
Enhanced error handling for the Property Management System.

Provides custom exceptions, error responses, and user-friendly error messages.
"""

import logging
from typing import Any, Dict, Optional
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from core.logging import logger

# Setup logger
error_logger = logging.getLogger('pms.errors')


class PMSException(APIException):
    """Base exception class for Property Management System errors."""

    def __init__(self, message: str, error_code: str = "", details: Optional[Dict[str, Any]] = None,
                 status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationException(PMSException):
    """Exception for validation errors."""
    status_code = status.HTTP_400_BAD_REQUEST


class PermissionDeniedException(PMSException):
    """Exception for permission denied errors."""
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundException(PMSException):
    """Exception for resource not found errors."""
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(PMSException):
    """Exception for resource conflict errors."""
    status_code = status.HTTP_409_CONFLICT


class PaymentException(PMSException):
    """Exception for payment processing errors."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED


class ExternalServiceException(PMSException):
    """Exception for external service errors."""
    status_code = status.HTTP_502_BAD_GATEWAY


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[JsonResponse]:
    """
    Custom DRF exception handler with enhanced error formatting.

    Provides consistent error responses across the API.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Enhance the response with additional error information
        error_data = {
            'success': False,
            'message': get_user_friendly_message(exc),
            'error_code': get_error_code(exc),
        }

        # Include original error details in development
        if hasattr(exc, 'detail'):
            error_data['details'] = exc.detail
        elif hasattr(exc, 'message'):
            error_data['details'] = exc.message

        # Add request context for debugging
        if context.get('request'):
            request = context['request']
            error_data['path'] = request.path
            error_data['method'] = request.method

        response.data = error_data

        # Log the error
        log_error(exc, context, response.status_code)

    return response


def get_user_friendly_message(exc: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    error_messages = {
        'ValidationError': 'The provided data is invalid. Please check your input.',
        'PermissionDenied': 'You do not have permission to perform this action.',
        'NotFound': 'The requested resource was not found.',
        'AuthenticationFailed': 'Invalid credentials. Please check your username and password.',
        'NotAuthenticated': 'Authentication is required to access this resource.',
        'Throttled': 'Too many requests. Please try again later.',
        'IntegrityError': 'This action would violate data integrity constraints.',
        'PaymentException': 'Payment processing failed. Please try again or contact support.',
        'ExternalServiceException': 'A required external service is currently unavailable.',
    }

    exc_type = type(exc).__name__
    return error_messages.get(exc_type, 'An unexpected error occurred. Please try again.')


def get_error_code(exc: Exception) -> str:
    """Get error code for exception."""
    if hasattr(exc, 'error_code'):
        return exc.error_code

    error_codes = {
        'ValidationError': 'VALIDATION_ERROR',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotFound': 'RESOURCE_NOT_FOUND',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'Throttled': 'RATE_LIMIT_EXCEEDED',
        'IntegrityError': 'DATA_INTEGRITY_ERROR',
    }

    return error_codes.get(type(exc).__name__, 'UNKNOWN_ERROR')


def log_error(exc: Exception, context: Dict[str, Any], status_code: int):
    """Log errors with appropriate severity."""
    error_data = {
        'exception_type': type(exc).__name__,
        'message': str(exc),
        'status_code': status_code,
        'path': context.get('request', {}).path if context.get('request') else None,
        'method': context.get('request', {}).method if context.get('request') else None,
        'user_id': context.get('request', {}).user.id if context.get('request') and hasattr(context['request'], 'user') else None,
    }

    if status_code >= 500:
        error_logger.error(f"Server error: {str(exc)}", extra={'extra_data': error_data}, exc_info=True)
    elif status_code >= 400:
        error_logger.warning(f"Client error: {str(exc)}", extra={'extra_data': error_data})
    else:
        error_logger.info(f"Request error: {str(exc)}", extra={'extra_data': error_data})


def handler404(request, exception=None):
    """
    Custom 404 error handler that returns a JSON response.
    """
    error_data = {
        'success': False,
        'message': 'The requested resource was not found.',
        'error_code': 'NOT_FOUND',
        'path': request.path,
        'method': request.method,
    }

    # Log 404 errors for monitoring
    error_logger.info(f"404 Not Found: {request.method} {request.path}", extra={
        'extra_data': {
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'referer': request.META.get('HTTP_REFERER'),
            'ip': request.META.get('REMOTE_ADDR'),
        }
    })

    return JsonResponse(error_data, status=status.HTTP_404_NOT_FOUND)


def handler500(request):
    """
    Custom 500 error handler that returns a JSON response.
    """
    error_data = {
        'success': False,
        'message': 'An unexpected error occurred on the server. Our team has been notified.',
        'error_code': 'INTERNAL_SERVER_ERROR',
        'path': request.path if request else None,
        'method': request.method if request else None,
    }

    # Log 500 errors with full context
    error_logger.error(f"500 Internal Server Error: {request.method} {request.path}", extra={
        'extra_data': {
            'user_agent': request.META.get('HTTP_USER_AGENT') if request else None,
            'user_id': request.user.id if request and hasattr(request, 'user') and request.user.is_authenticated else None,
        }
    }, exc_info=True)

    return JsonResponse(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ErrorNotification:
    """Utility class for sending error notifications."""

    @staticmethod
    def notify_admin_error(error: Exception, context: Dict[str, Any] = None):
        """Send notification to admins about critical errors."""
        try:
            from core.notifications import send_admin_notification

            message = f"""
            Critical Error Alert:

            Error: {type(error).__name__}
            Message: {str(error)}
            Context: {context or {}}

            This error has been logged and requires immediate attention.
            """

            send_admin_notification("Critical System Error", message)
        except Exception as notification_error:
            error_logger.error(f"Failed to send admin notification: {str(notification_error)}")

    @staticmethod
    def notify_user_error(user_id: int, error_message: str, action: str = "operation"):
        """Send user-friendly error notification to user."""
        try:
            from core.notifications import send_user_notification

            message = f"""
            We encountered an issue while processing your {action}.

            Error: {error_message}

            Please try again, or contact support if the problem persists.
            """

            send_user_notification(user_id, f"Issue with {action.title()}", message)
        except Exception as notification_error:
            error_logger.error(f"Failed to send user notification: {str(notification_error)}")


def validate_request_data(data: Dict[str, Any], required_fields: list, field_validators: Dict[str, callable] = None) -> Dict[str, str]:
    """
    Validate request data and return field-specific errors.

    Args:
        data: Request data dictionary
        required_fields: List of required field names
        field_validators: Optional dict of field name -> validator function

    Returns:
        Dictionary of field errors
    """
    errors = {}

    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field.replace('_', ' ').title()} is required."

    # Run custom validators
    if field_validators:
        for field, validator in field_validators.items():
            if field in data:
                try:
                    validator(data[field])
                except ValidationError as e:
                    errors[field] = str(e)

    return errors
