"""
Custom exception handlers for Django REST Framework.
Provides user-friendly error messages instead of technical jargon.
"""

from typing import Any, Dict
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


class UserFriendlyAPIException(APIException):
    """Base class for user-friendly API exceptions"""

    def __init__(self, detail: str = None, code: str = None):
        # Use user-friendly messages instead of technical ones
        if detail is None:
            detail = "Something went wrong. Please try again."
        super().__init__(detail, code)


def get_user_friendly_error_message(exc: Exception) -> str:
    """
    Convert technical error messages to user-friendly ones
    """

    # Handle specific exception types
    if isinstance(exc, NotAuthenticated):
        return "Please sign in to continue."

    elif isinstance(exc, AuthenticationFailed):
        return "Invalid email or password. Please check your credentials."

    elif isinstance(exc, PermissionDenied):
        return "You don't have permission to perform this action."

    elif isinstance(exc, NotFound):
        return "The item you're looking for doesn't exist."

    elif isinstance(exc, MethodNotAllowed):
        return "This action is not allowed."

    elif isinstance(exc, Throttled):
        return "You're making requests too quickly. Please wait a moment before trying again."

    elif isinstance(exc, ValidationError):
        # Handle DRF validation errors
        return "Please check your information and try again."

    elif isinstance(exc, DjangoValidationError):
        # Handle Django model validation errors
        return "Please check your information and try again."

    elif isinstance(exc, IntegrityError):
        # Handle database constraint violations
        error_msg = str(exc).lower()
        if 'unique constraint' in error_msg or 'duplicate key' in error_msg:
            return "This information is already in use. Please try different values."
        elif 'foreign key' in error_msg:
            return "Cannot complete this action due to related data dependencies."
        else:
            return "Database error occurred. Please try again."

    elif isinstance(exc, ConnectionError) or isinstance(exc, TimeoutError):
        return "Connection issue. Please check your internet and try again."

    # Handle HTTP status codes with custom messages
    if hasattr(exc, 'status_code'):
        status_messages = {
            status.HTTP_400_BAD_REQUEST: "Please check your information and try again.",
            status.HTTP_401_UNAUTHORIZED: "Your session has expired. Please sign in again.",
            status.HTTP_403_FORBIDDEN: "You don't have permission to perform this action.",
            status.HTTP_404_NOT_FOUND: "The item you're looking for doesn't exist.",
            status.HTTP_405_METHOD_NOT_ALLOWED: "This action is not allowed.",
            status.HTTP_409_CONFLICT: "This action conflicts with existing data.",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "Please check your information - some details are invalid.",
            status.HTTP_429_TOO_MANY_REQUESTS: "You're making requests too quickly. Please wait a moment.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Something went wrong on our end. Please try again.",
            status.HTTP_502_BAD_GATEWAY: "Service is temporarily unavailable. Please try again.",
            status.HTTP_503_SERVICE_UNAVAILABLE: "Service is temporarily unavailable. Please try again.",
            status.HTTP_504_GATEWAY_TIMEOUT: "Request timed out. Please try again.",
        }

        return status_messages.get(exc.status_code, "Something went wrong. Please try again.")

    # Default fallback
    return "Something went wrong. Please try again."


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Custom exception handler that provides user-friendly error messages
    """

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Get user-friendly message
        user_friendly_message = get_user_friendly_error_message(exc)

        # Handle validation errors specially
        if isinstance(exc, ValidationError):
            # Keep field-specific validation errors but make them user-friendly
            user_friendly_data = {}

            for field, messages in response.data.items():
                if isinstance(messages, list):
                    # Convert technical validation messages to user-friendly ones
                    friendly_messages = []
                    for message in messages:
                        if isinstance(message, str):
                            # Map common validation messages
                            friendly_message = message
                            if 'required' in message.lower():
                                friendly_message = 'This field is required.'
                            elif 'invalid' in message.lower():
                                friendly_message = 'Please enter valid information.'
                            elif 'max_length' in message.lower():
                                friendly_message = 'This text is too long.'
                            elif 'min_value' in message.lower():
                                friendly_message = 'This value is too small.'
                            elif 'max_value' in message.lower():
                                friendly_message = 'This value is too large.'
                            elif 'unique' in message.lower():
                                friendly_message = 'This value is already in use.'

                            friendly_messages.append(friendly_message)

                    user_friendly_data[field] = friendly_messages
                else:
                    user_friendly_data[field] = messages

            response.data = user_friendly_data

        elif isinstance(exc, DjangoValidationError):
            # Handle Django model validation errors
            response.data = {
                'detail': user_friendly_message,
                'errors': str(exc)
            }

        else:
            # For other errors, replace the detail with user-friendly message
            if 'detail' in response.data:
                response.data['detail'] = user_friendly_message
            else:
                response.data = {
                    'detail': user_friendly_message
                }

    return response