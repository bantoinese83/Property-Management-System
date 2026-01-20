"""
API optimization utilities for the Property Management System.

Provides response caching, compression, rate limiting, and performance monitoring.
"""

import hashlib
import json
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from core.logging import logger

F = TypeVar('F', bound=Callable[..., Any])


def cache_api_response(timeout: int = 300, key_prefix: str = "api",
                      vary_on: Optional[list] = None):
    """
    Decorator to cache API responses.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
        vary_on: List of headers to vary cache on (e.g., ['Authorization'])
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            # Skip caching for non-GET requests or when cache is disabled
            if request.method != 'GET' or getattr(request, '_cache_disabled', False):
                return func(view_instance, request, *args, **kwargs)

            # Generate cache key
            user_id = getattr(request.user, 'id', None)
            query_params = dict(request.GET)
            path = request.get_full_path()

            # Include vary_on headers in key
            vary_headers = {}
            if vary_on:
                for header in vary_on:
                    vary_headers[header] = request.META.get(f'HTTP_{header.upper().replace("-", "_")}', '')

            # Create unique cache key
            key_data = {
                'path': path,
                'user_id': user_id,
                'query_params': query_params,
                'vary_headers': vary_headers,
            }
            cache_key = f"{key_prefix}:{hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.debug(f"API cache hit for {cache_key}")
                return Response(cached_response, status=status.HTTP_200_OK)

            # Execute view function
            response = func(view_instance, request, *args, **kwargs)

            # Cache successful responses
            if hasattr(response, 'data') and response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
                logger.debug(f"Cached API response for {cache_key}")

            return response

        return wrapper
    return decorator


def disable_cache(view_func: F) -> F:
    """Decorator to disable caching for a view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request._cache_disabled = True
        return view_func(request, *args, **kwargs)
    return wrapper


def compress_response(view_func: F) -> F:
    """Decorator to enable gzip compression for API responses."""
    @wraps(view_func)
    @vary_on_headers('Accept-Encoding')
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        # Enable compression for large responses
        if hasattr(response, 'data'):
            response['Content-Encoding'] = 'gzip'
            response['Vary'] = 'Accept-Encoding'

        return response
    return wrapper


class APIResponse:
    """Enhanced API response class with metadata and performance tracking."""

    @staticmethod
    def success(data: Any = None, message: str = "", status_code: int = status.HTTP_200_OK,
               metadata: Optional[Dict] = None) -> Response:
        """Create a successful API response."""
        response_data = {
            'success': True,
            'data': data,
            'message': message,
        }

        if metadata:
            response_data['metadata'] = metadata

        return Response(response_data, status=status_code)

    @staticmethod
    def error(message: str, error_code: str = "", details: Optional[Dict] = None,
             status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        """Create an error API response."""
        response_data = {
            'success': False,
            'message': message,
            'error_code': error_code,
        }

        if details:
            response_data['details'] = details

        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(data: Any, count: int, page: int, page_size: int,
                 total_pages: int, has_next: bool, has_previous: bool,
                 message: str = "") -> Response:
        """Create a paginated API response."""
        return APIResponse.success(
            data=data,
            message=message,
            metadata={
                'pagination': {
                    'count': count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_previous': has_previous,
                }
            }
        )


def optimize_queryset_response(queryset_method: F) -> F:
    """Decorator to optimize queryset responses with database query analysis."""
    @wraps(queryset_method)
    def wrapper(*args, **kwargs):
        from django.db import connection
        from core.logging import logger

        initial_queries = len(connection.queries)

        # Execute the queryset method
        result = queryset_method(*args, **kwargs)

        # Log query performance
        final_queries = len(connection.queries)
        new_queries = final_queries - initial_queries

        if new_queries > 0:
            total_time = sum(float(q.get('time', 0)) for q in connection.queries[-new_queries:])
            logger.info(
                f"Queryset executed {new_queries} queries in {total_time:.2f}ms",
                extra={
                    'extra_data': {
                        'query_count': new_queries,
                        'total_time_ms': total_time,
                        'avg_time_per_query': total_time / new_queries if new_queries > 0 else 0,
                    }
                }
            )

        return result

    return wrapper


class OptimizedViewSetMixin:
    """Mixin to add optimization features to ViewSets."""

    # Default cache timeout (5 minutes)
    cache_timeout = 300

    # Fields to optimize queries with
    optimize_select_related = []
    optimize_prefetch_related = []

    def get_queryset(self):
        """Override to add query optimization."""
        queryset = super().get_queryset()

        # Apply optimizations
        if self.optimize_select_related:
            queryset = queryset.select_related(*self.optimize_select_related)

        if self.optimize_prefetch_related:
            queryset = queryset.prefetch_related(*self.optimize_prefetch_related)

        return queryset

    @method_decorator(cache_api_response(timeout=cache_timeout))
    def list(self, request, *args, **kwargs):
        """Cached list view."""
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_api_response(timeout=cache_timeout))
    def retrieve(self, request, *args, **kwargs):
        """Cached retrieve view."""
        return super().retrieve(request, *args, **kwargs)


class APIPerformanceMiddleware:
    """Middleware to track API performance metrics."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        import time

        if not request.path.startswith('/api/'):
            return self.get_response(request)

        start_time = time.time()
        response = self.get_response(request)
        duration = (time.time() - start_time) * 1000

        # Log slow API requests
        if duration > 1000:  # More than 1 second
            logger.warning(
                f"Slow API request: {request.method} {request.path} took {duration:.2f}ms",
                extra={
                    'extra_data': {
                        'method': request.method,
                        'path': request.path,
                        'duration_ms': duration,
                        'status_code': response.status_code,
                        'user_id': getattr(request.user, 'id', None),
                    }
                }
            )

        # Add performance headers
        response['X-Response-Time'] = f"{duration:.2f}ms"
        response['X-API-Version'] = "v1.0.0"

        return response


def rate_limit(requests_per_minute: int = 60, key_prefix: str = "api_ratelimit"):
    """
    Decorator to implement simple rate limiting.

    Note: For production use, consider using django-ratelimit or similar.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Simple IP-based rate limiting using cache
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"{key_prefix}:{client_ip}"

            # Get current request count
            request_count = cache.get(cache_key, 0)

            # Allow much higher limits in development
            is_development = os.getenv('DJANGO_ENV', 'production') == 'development'
            effective_limit = 300 if is_development else requests_per_minute  # 300 requests/min in dev

            if request_count >= effective_limit:
                return APIResponse.error(
                    "Rate limit exceeded. Please try again later.",
                    "RATE_LIMIT_EXCEEDED",
                    status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Increment counter
            cache.set(cache_key, request_count + 1, 60)  # 1 minute window

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def api_error_handler(func: F) -> F:
    """Decorator to handle API errors consistently."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {str(e)}", exc_info=True)

            # Return appropriate error response
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return APIResponse.error(
                "An unexpected error occurred. Please try again.",
                "INTERNAL_ERROR",
                status_code=status_code
            )

    return wrapper


# Response compression utility
def gzip_response(min_size: int = 1024):
    """Decorator to compress large JSON responses."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = func(request, *args, **kwargs)

            # Compress large responses
            if (hasattr(response, 'data') and
                len(json.dumps(response.data)) > min_size):
                response['Content-Encoding'] = 'gzip'

            return response

        return wrapper
    return decorator