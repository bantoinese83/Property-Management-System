"""
Core utilities for the Property Management System.

This module provides essential utilities for:
- Database optimization and caching
- API response handling and caching
- Logging and monitoring
- Error handling and exceptions
- Health checks and metrics
- Performance monitoring
"""

# Import key utilities for easy access
from .api_utils import (
    APIResponse,
    OptimizedViewSetMixin,
    api_error_handler,
    cache_api_response,
    compress_response,
    rate_limit,
)
from .db_utils import (
    QueryOptimizer,
    analyze_table_performance,
    bulk_create_with_progress,
    cache_queryset,
    create_composite_index,
    get_or_create_with_cache,
    log_slow_queries,
    optimize_queryset,
)
from .exceptions import (
    ConflictException,
    ErrorNotification,
    ExternalServiceException,
    NotFoundException,
    PaymentException,
    PermissionDeniedException,
    PMSException,
    ValidationException,
    custom_exception_handler,
    validate_request_data,
)
from .logging import (
    PerformanceMonitor,
    RequestLogger,
    log_database_query,
    log_error,
    log_performance,
    log_security_event,
    setup_logging,
)

# Version information
__version__ = "1.0.0"
__all__ = [
    # API utilities
    "APIResponse",
    "OptimizedViewSetMixin",
    "cache_api_response",
    "compress_response",
    "rate_limit",
    "api_error_handler",
    # Database utilities
    "QueryOptimizer",
    "cache_queryset",
    "optimize_queryset",
    "log_slow_queries",
    "bulk_create_with_progress",
    "get_or_create_with_cache",
    "create_composite_index",
    "analyze_table_performance",
    # Exception handling
    "PMSException",
    "ValidationException",
    "PermissionDeniedException",
    "NotFoundException",
    "ConflictException",
    "PaymentException",
    "ExternalServiceException",
    "custom_exception_handler",
    "ErrorNotification",
    "validate_request_data",
    # Logging and monitoring
    "setup_logging",
    "RequestLogger",
    "log_performance",
    "log_database_query",
    "log_error",
    "log_security_event",
    "PerformanceMonitor",
]
