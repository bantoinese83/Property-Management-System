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
    cache_api_response,
    compress_response,
    rate_limit,
    api_error_handler,
)

from .db_utils import (
    QueryOptimizer,
    cache_queryset,
    optimize_queryset,
    log_slow_queries,
    bulk_create_with_progress,
    get_or_create_with_cache,
    create_composite_index,
    analyze_table_performance,
)

from .exceptions import (
    PMSException,
    ValidationException,
    PermissionDeniedException,
    NotFoundException,
    ConflictException,
    PaymentException,
    ExternalServiceException,
    custom_exception_handler,
    ErrorNotification,
    validate_request_data,
)

from .logging import (
    setup_logging,
    RequestLogger,
    log_performance,
    log_database_query,
    log_error,
    log_security_event,
    PerformanceMonitor,
)

# Version information
__version__ = "1.0.0"
__all__ = [
    # API utilities
    'APIResponse',
    'OptimizedViewSetMixin',
    'cache_api_response',
    'compress_response',
    'rate_limit',
    'api_error_handler',

    # Database utilities
    'QueryOptimizer',
    'cache_queryset',
    'optimize_queryset',
    'log_slow_queries',
    'bulk_create_with_progress',
    'get_or_create_with_cache',
    'create_composite_index',
    'analyze_table_performance',

    # Exception handling
    'PMSException',
    'ValidationException',
    'PermissionDeniedException',
    'NotFoundException',
    'ConflictException',
    'PaymentException',
    'ExternalServiceException',
    'custom_exception_handler',
    'ErrorNotification',
    'validate_request_data',

    # Logging and monitoring
    'setup_logging',
    'RequestLogger',
    'log_performance',
    'log_database_query',
    'log_error',
    'log_security_event',
    'PerformanceMonitor',
]