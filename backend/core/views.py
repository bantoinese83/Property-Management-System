"""
Health check and monitoring views for the Property Management System.
"""

import psutil
import os
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from core.logging import logger, PerformanceMonitor


@never_cache
@require_GET
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Comprehensive health check endpoint.

    Returns detailed health status of all system components.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': None,  # Will be set by middleware
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development',
        'checks': {}
    }

    try:
        # Database health check
        db_status = check_database()
        health_status['checks']['database'] = db_status

        # Redis/Cache health check
        cache_status = check_cache()
        health_status['checks']['cache'] = cache_status

        # File system health check
        fs_status = check_file_system()
        health_status['checks']['filesystem'] = fs_status

        # Memory health check
        memory_status = check_memory()
        health_status['checks']['memory'] = memory_status

        # Disk space check
        disk_status = check_disk_space()
        health_status['checks']['disk'] = disk_status

        # External services check
        external_status = check_external_services()
        health_status['checks']['external_services'] = external_status

        # Determine overall status
        all_healthy = all(
            check.get('status') == 'healthy'
            for check in health_status['checks'].values()
        )

        if not all_healthy:
            health_status['status'] = 'unhealthy'
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info("Health check completed successfully", extra={
            'extra_data': {'health_status': health_status}
        })

        return Response(health_status, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        health_status['status'] = 'error'
        health_status['error'] = str(e)
        return Response(health_status, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@never_cache
@require_GET
@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check for Kubernetes/load balancer.

    Returns 200 if the application is ready to serve traffic.
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        if result and result[0] == 1:
            return Response({'status': 'ready'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'not ready'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return Response({'status': 'not ready', 'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@never_cache
@require_GET
@api_view(['GET'])
def metrics(request):
    """
    Application metrics endpoint.

    Returns performance metrics and statistics.
    Requires authentication in production.
    """
    try:
        metrics_data = {
            'database': get_database_metrics(),
            'cache': get_cache_metrics(),
            'system': get_system_metrics(),
            'application': get_application_metrics(),
        }

        return Response(metrics_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_database():
    """Check database connectivity and performance."""
    try:
        with connection.cursor() as cursor:
            # Test basic connectivity
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()

            if result and result[0] == 1:
                # Test query performance
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                migration_count = cursor.fetchone()[0]

                return {
                    'status': 'healthy',
                    'details': {
                        'connection': 'successful',
                        'migrations': migration_count,
                        'database_name': connection.settings_dict.get('NAME', 'unknown'),
                        'engine': connection.vendor,
                    }
                }
            else:
                return {'status': 'unhealthy', 'error': 'Database query failed'}

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_cache():
    """Check Redis/cache connectivity."""
    try:
        # Test cache set/get
        test_key = 'health_check_test'
        test_value = 'ok'

        cache.set(test_key, test_value, 10)
        retrieved_value = cache.get(test_key)

        if retrieved_value == test_value:
            cache.delete(test_key)
            return {
                'status': 'healthy',
                'details': {
                    'cache_backend': cache.__class__.__name__,
                    'connection': 'successful',
                }
            }
        else:
            return {'status': 'unhealthy', 'error': 'Cache set/get failed'}

    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_file_system():
    """Check file system permissions and space."""
    try:
        # Check media directory
        media_dir = settings.MEDIA_ROOT
        if not os.path.exists(media_dir):
            os.makedirs(media_dir, exist_ok=True)

        # Test write permissions
        test_file = os.path.join(media_dir, 'health_check.tmp')
        with open(test_file, 'w') as f:
            f.write('test')

        os.remove(test_file)

        return {
            'status': 'healthy',
            'details': {
                'media_root': media_dir,
                'permissions': 'writable',
            }
        }

    except Exception as e:
        logger.error(f"File system health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


def check_memory():
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Consider unhealthy if memory usage > 90%
        if memory_percent > 90:
            return {
                'status': 'warning',
                'details': {
                    'usage_percent': memory_percent,
                    'available_mb': memory.available / (1024 * 1024),
                    'warning': 'High memory usage detected'
                }
            }

        return {
            'status': 'healthy',
            'details': {
                'usage_percent': memory_percent,
                'total_mb': memory.total / (1024 * 1024),
                'available_mb': memory.available / (1024 * 1024),
            }
        }

    except Exception as e:
        logger.warning(f"Memory check failed: {str(e)}")
        return {'status': 'unknown', 'error': str(e)}


def check_disk_space():
    """Check disk space availability."""
    try:
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        # Consider unhealthy if disk usage > 90%
        if disk_percent > 90:
            return {
                'status': 'warning',
                'details': {
                    'usage_percent': disk_percent,
                    'free_gb': disk.free / (1024 * 1024 * 1024),
                    'warning': 'Low disk space detected'
                }
            }

        return {
            'status': 'healthy',
            'details': {
                'usage_percent': disk_percent,
                'total_gb': disk.total / (1024 * 1024 * 1024),
                'free_gb': disk.free / (1024 * 1024 * 1024),
            }
        }

    except Exception as e:
        logger.warning(f"Disk space check failed: {str(e)}")
        return {'status': 'unknown', 'error': str(e)}


def check_external_services():
    """Check external service connectivity."""
    external_checks = {}

    # Check email configuration (if SMTP is configured)
    if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
        try:
            import smtplib
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT or 587, timeout=5)
            server.quit()
            external_checks['email'] = {'status': 'healthy', 'service': 'SMTP'}
        except Exception as e:
            external_checks['email'] = {'status': 'unhealthy', 'error': str(e)}

    # Add more external service checks here (Stripe, AWS, etc.)

    return external_checks


def get_database_metrics():
    """Get detailed database metrics."""
    try:
        with connection.cursor() as cursor:
            # Get table counts
            cursor.execute("""
                SELECT table_name, (SELECT n_tup_ins - n_tup_del FROM pg_stat_user_tables WHERE relname = table_name) as row_count
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)

            tables = {row[0]: row[1] for row in cursor.fetchall()}

            # Get database size
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            db_size = cursor.fetchone()[0]

            return {
                'table_counts': tables,
                'database_size': db_size,
                'connection_count': len(connection.queries) if hasattr(connection, 'queries') else 0,
            }

    except Exception as e:
        logger.error(f"Database metrics collection failed: {str(e)}")
        return {'error': str(e)}


def get_cache_metrics():
    """Get cache performance metrics."""
    try:
        # This would be more detailed if using Redis directly
        return {
            'backend': cache.__class__.__name__,
            'stats': getattr(cache, 'get_stats', lambda: {})(),
        }
    except Exception as e:
        logger.error(f"Cache metrics collection failed: {str(e)}")
        return {'error': str(e)}


def get_system_metrics():
    """Get system-level metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            'cpu_percent': cpu_percent,
            'memory': {
                'total_mb': memory.total / (1024 * 1024),
                'available_mb': memory.available / (1024 * 1024),
                'usage_percent': memory.percent,
            },
            'disk': {
                'total_gb': disk.total / (1024 * 1024 * 1024),
                'free_gb': disk.free / (1024 * 1024 * 1024),
                'usage_percent': disk.percent,
            },
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
        }

    except Exception as e:
        logger.error(f"System metrics collection failed: {str(e)}")
        return {'error': str(e)}


def get_application_metrics():
    """Get application-specific metrics."""
    try:
        # This would integrate with Django's stats collection
        # For now, return basic app info
        return {
            'django_version': getattr(settings, 'VERSION', 'unknown'),
            'debug_mode': settings.DEBUG,
            'installed_apps_count': len(settings.INSTALLED_APPS),
            'middleware_count': len(settings.MIDDLEWARE),
            'database_connections': len(settings.DATABASES),
        }

    except Exception as e:
        logger.error(f"Application metrics collection failed: {str(e)}")
        return {'error': str(e)}