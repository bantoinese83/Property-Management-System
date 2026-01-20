"""
Comprehensive logging utilities for the Property Management System.

Provides structured logging with different levels, request tracking,
performance monitoring, and error handling.
"""

import logging
import json
import time
import uuid
from functools import wraps
from typing import Any, Dict, Optional
from django.conf import settings
from django.http import HttpRequest
from django.db import connection


# Configure structured logging
class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Add structured fields
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)

        # Add request info if present
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        # Add user info if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id

        # Add performance info if present
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration

        # Add error info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        if settings.DEBUG:
            return json.dumps(log_entry, indent=2, default=str)
        return json.dumps(log_entry, default=str)


def setup_logging():
    """Configure application-wide logging."""
    # Create logger
    logger = logging.getLogger('pms')
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)

    # File handler for production
    if not settings.DEBUG:
        file_handler = logging.FileHandler('logs/pms.log')
        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(logging.WARNING)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logging()


class RequestLogger:
    """Middleware for logging HTTP requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        start_time = time.time()

        # Log request start
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'extra_data': {
                    'method': request.method,
                    'path': request.path,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'ip': self.get_client_ip(request),
                    'query_params': dict(request.GET),
                },
                'request_id': request_id,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            }
        )

        # Process request
        response = self.get_response(request)

        # Calculate duration
        duration = (time.time() - start_time) * 1000

        # Log request completion
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO

        logger.log(
            log_level,
            f"Request completed: {response.status_code} in {duration:.2f}ms",
            extra={
                'extra_data': {
                    'status_code': response.status_code,
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                    'db_queries': len(connection.queries) if settings.DEBUG else None,
                },
                'request_id': request_id,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'duration': duration,
            }
        )

        return response

    def get_client_ip(self, request: HttpRequest) -> str:
        """Get the client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


def log_performance(func):
    """Decorator to log function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start_time) * 1000

        logger.info(
            f"Function {func.__name__} completed in {duration:.2f}ms",
            extra={
                'extra_data': {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs),
                },
                'duration': duration,
            }
        )

        return result
    return wrapper


def log_database_query(func):
    """Decorator to log database query performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        initial_queries = len(connection.queries)
        start_time = time.time()

        result = func(*args, **kwargs)

        query_count = len(connection.queries) - initial_queries
        duration = (time.time() - start_time) * 1000

        if query_count > 0:
            logger.info(
                f"Database operation: {query_count} queries in {duration:.2f}ms",
                extra={
                    'extra_data': {
                        'function': func.__name__,
                        'query_count': query_count,
                        'avg_query_time': duration / query_count if query_count > 0 else 0,
                    },
                    'duration': duration,
                }
            )

        return result
    return wrapper


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an error with context."""
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            'extra_data': {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {},
            }
        },
        exc_info=True
    )


def log_security_event(event: str, user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
    """Log security-related events."""
    logger.warning(
        f"Security event: {event}",
        extra={
            'extra_data': {
                'event_type': 'security',
                'event': event,
                'details': details or {},
            },
            'user_id': user_id,
        }
    )


# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor application performance metrics."""

    @staticmethod
    def log_slow_query(query: str, duration: float, params: Optional[Dict] = None):
        """Log slow database queries."""
        logger.warning(
            f"Slow query detected: {duration:.2f}ms",
            extra={
                'extra_data': {
                    'query_type': 'slow_query',
                    'query': query[:500],  # Truncate long queries
                    'duration_ms': duration,
                    'params': params,
                }
            }
        )

    @staticmethod
    def log_memory_usage():
        """Log current memory usage."""
        import psutil
        import os

        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            logger.info(
                "Memory usage stats",
                extra={
                    'extra_data': {
                        'memory_rss': memory_info.rss,
                        'memory_vms': memory_info.vms,
                        'memory_percent': process.memory_percent(),
                    }
                }
            )
        except ImportError:
            logger.debug("psutil not available for memory monitoring")

    @staticmethod
    def log_cache_stats(hits: int, misses: int):
        """Log cache performance statistics."""
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        logger.info(
            f"Cache stats: {hits} hits, {misses} misses ({hit_rate:.1f}% hit rate)",
            extra={
                'extra_data': {
                    'cache_hits': hits,
                    'cache_misses': misses,
                    'cache_hit_rate': hit_rate,
                }
            }
        )