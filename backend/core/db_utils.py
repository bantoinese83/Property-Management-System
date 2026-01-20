"""
Database optimization utilities for the Property Management System.

Provides query optimization, caching, and performance monitoring tools.
"""

from functools import wraps
from typing import Any, Callable, Optional, TypeVar
from django.core.cache import cache
from django.db import connection, models
from django.db.models import QuerySet, Prefetch
from django.utils.decorators import method_decorator
from core.logging import logger, log_database_query

F = TypeVar('F', bound=Callable[..., Any])


def optimize_queryset(queryset: QuerySet, select_related: Optional[list] = None,
                     prefetch_related: Optional[list] = None,
                     defer: Optional[list] = None, only: Optional[list] = None) -> QuerySet:
    """
    Optimize a queryset with select_related, prefetch_related, defer, and only.

    Args:
        queryset: The queryset to optimize
        select_related: Fields to select_related (for ForeignKey relationships)
        prefetch_related: Fields to prefetch_related (for reverse ForeignKey/ManyToMany)
        defer: Fields to defer loading
        only: Fields to load exclusively

    Returns:
        Optimized queryset
    """
    if select_related:
        queryset = queryset.select_related(*select_related)

    if prefetch_related:
        # Handle nested prefetching
        prefetch_objects = []
        for prefetch in prefetch_related:
            if isinstance(prefetch, str):
                prefetch_objects.append(prefetch)
            elif isinstance(prefetch, Prefetch):
                prefetch_objects.append(prefetch)

        queryset = queryset.prefetch_related(*prefetch_objects)

    if defer:
        queryset = queryset.defer(*defer)

    if only:
        queryset = queryset.only(*only)

    return queryset


def cache_queryset(timeout: int = 300, key_prefix: str = ""):
    """
    Decorator to cache queryset results.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys to avoid conflicts
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cached result for {cache_key}")

            return result
        return wrapper
    return decorator


class QueryOptimizer:
    """Utility class for database query optimization."""

    @staticmethod
    def get_property_with_details(property_id: int) -> Optional[models.Model]:
        """Get a property with optimized related data loading."""
        return optimize_queryset(
            queryset=models.Property.objects.filter(id=property_id),
            select_related=['owner'],
            prefetch_related=[
                'leases__tenant',
                'maintenance_requests',
                Prefetch('documents', queryset=models.Document.objects.filter(is_active=True))
            ]
        ).first()

    @staticmethod
    def get_tenant_with_leases(tenant_id: int) -> Optional[models.Model]:
        """Get a tenant with optimized lease data."""
        return optimize_queryset(
            queryset=models.Tenant.objects.filter(id=tenant_id),
            prefetch_related=[
                'leases__property',
                'payments',
                Prefetch('documents', queryset=models.Document.objects.filter(is_active=True))
            ]
        ).first()

    @staticmethod
    def get_lease_with_full_details(lease_id: int) -> Optional[models.Model]:
        """Get a lease with all related data optimized."""
        return optimize_queryset(
            queryset=models.Lease.objects.filter(id=lease_id),
            select_related=['property', 'tenant'],
            prefetch_related=[
                'payments',
                'maintenance_requests',
                Prefetch('property__documents', queryset=models.Document.objects.filter(is_active=True)),
                Prefetch('tenant__documents', queryset=models.Document.objects.filter(is_active=True))
            ]
        ).first()

    @staticmethod
    def get_dashboard_stats(user_id: Optional[int] = None) -> dict:
        """Get dashboard statistics with optimized queries."""
        from django.db.models import Count, Sum, Q
        from properties.models import Property
        from tenants.models import Tenant
        from leases.models import Lease
        from payments.models import RentPayment

        # Use select_related and annotations to minimize queries
        stats = {}

        # Property stats
        property_queryset = Property.objects.all()
        if user_id:
            property_queryset = property_queryset.filter(owner_id=user_id)

        stats['properties'] = {
            'total': property_queryset.count(),
            'occupied': property_queryset.filter(
                leases__lease_end_date__gte=models.functions.Now()
            ).distinct().count(),
        }

        # Tenant stats
        tenant_queryset = Tenant.objects.all()
        if user_id:
            tenant_queryset = tenant_queryset.filter(
                leases__property__owner_id=user_id
            ).distinct()

        stats['tenants'] = {
            'total': tenant_queryset.count(),
            'active': tenant_queryset.filter(
                leases__lease_end_date__gte=models.functions.Now()
            ).distinct().count(),
        }

        # Financial stats (last 30 days)
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        payment_queryset = RentPayment.objects.filter(
            created_at__gte=thirty_days_ago
        )

        if user_id:
            payment_queryset = payment_queryset.filter(
                lease__property__owner_id=user_id
            )

        stats['payments'] = {
            'total_amount': payment_queryset.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'count': payment_queryset.count(),
        }

        # Maintenance stats
        from maintenance.models import MaintenanceRequest
        maintenance_queryset = MaintenanceRequest.objects.all()
        if user_id:
            maintenance_queryset = maintenance_queryset.filter(
                property__owner_id=user_id
            )

        stats['maintenance'] = {
            'total': maintenance_queryset.count(),
            'pending': maintenance_queryset.filter(status='pending').count(),
            'in_progress': maintenance_queryset.filter(status='in_progress').count(),
        }

        return stats


def log_slow_queries(threshold_ms: float = 1000):
    """
    Log database queries that exceed the threshold time.

    Usage:
        with log_slow_queries():
            # Your database operations here
            pass
    """
    class SlowQueryLogger:
        def __enter__(self):
            self.initial_queries = len(connection.queries)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            final_queries = len(connection.queries)
            new_queries = connection.queries[self.initial_queries:]

            for query in new_queries:
                duration = float(query.get('time', 0))
                if duration > threshold_ms:
                    logger.warning(
                        f"Slow query detected: {duration:.2f}ms",
                        extra={
                            'extra_data': {
                                'query': query.get('sql', ''),
                                'duration_ms': duration,
                                'params': query.get('params', []),
                            }
                        }
                    )

    return SlowQueryLogger()


def bulk_create_with_progress(queryset: QuerySet, batch_size: int = 1000,
                             progress_callback: Optional[Callable] = None) -> int:
    """
    Bulk create objects with progress tracking.

    Args:
        queryset: Queryset to evaluate
        batch_size: Number of objects to create at once
        progress_callback: Optional callback function for progress updates

    Returns:
        Total number of objects created
    """
    total_created = 0
    batch = []

    for obj in queryset.iterator():
        batch.append(obj)

        if len(batch) >= batch_size:
            created_objects = queryset.model.objects.bulk_create(batch)
            total_created += len(created_objects)
            batch = []

            if progress_callback:
                progress_callback(total_created)

    # Create remaining objects
    if batch:
        created_objects = queryset.model.objects.bulk_create(batch)
        total_created += len(created_objects)

        if progress_callback:
            progress_callback(total_created)

    logger.info(f"Bulk created {total_created} objects of type {queryset.model.__name__}")
    return total_created


def get_or_create_with_cache(model: type[models.Model], defaults: dict = None,
                           timeout: int = 300, **kwargs) -> tuple[models.Model, bool]:
    """
    Cached version of get_or_create to reduce database hits.

    Args:
        model: Django model class
        defaults: Default values for creation
        timeout: Cache timeout in seconds
        **kwargs: Lookup parameters

    Returns:
        Tuple of (object, created)
    """
    # Create cache key from model and lookup parameters
    cache_key = f"get_or_create:{model.__name__}:{hash(str(sorted(kwargs.items())))}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.debug(f"Cache hit for get_or_create: {model.__name__}")
        return cached_result

    # Fall back to database
    obj, created = model.objects.get_or_create(defaults=defaults or {}, **kwargs)

    # Cache the result
    cache.set(cache_key, (obj, created), timeout)

    return obj, created


# Database index optimization helpers
def create_composite_index(model: type[models.Model], fields: list[str], name: str = None) -> str:
    """
    Generate SQL for creating a composite index.

    Args:
        model: Django model class
        fields: List of field names to include in the index
        name: Optional index name

    Returns:
        SQL statement for creating the index
    """
    if name is None:
        name = f"idx_{model._meta.db_table}_{'_'.join(fields)}"

    table_name = model._meta.db_table
    field_list = ', '.join(fields)

    sql = f"CREATE INDEX CONCURRENTLY {name} ON {table_name} ({field_list});"
    return sql


def analyze_table_performance(model: type[models.Model]) -> dict:
    """
    Analyze table performance and suggest optimizations.

    Returns:
        Dictionary with performance analysis and recommendations
    """
    table_name = model._meta.db_table
    analysis = {
        'table_name': table_name,
        'recommendations': [],
        'metrics': {}
    }

    try:
        with connection.cursor() as cursor:
            # Get table statistics
            cursor.execute(f"""
                SELECT
                    schemaname, tablename, seq_scan, seq_tup_read,
                    idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del
                FROM pg_stat_user_tables
                WHERE tablename = %s
            """, [table_name])

            stats = cursor.fetchone()
            if stats:
                analysis['metrics'] = {
                    'sequential_scans': stats[2],
                    'sequential_tuples_read': stats[3],
                    'index_scans': stats[4],
                    'index_tuples_fetched': stats[5],
                    'tuples_inserted': stats[6],
                    'tuples_updated': stats[7],
                    'tuples_deleted': stats[8],
                }

                # Generate recommendations
                seq_scans = stats[2] or 0
                idx_scans = stats[4] or 0

                if seq_scans > idx_scans * 10:  # More sequential than index scans
                    analysis['recommendations'].append(
                        "Consider adding indexes on frequently queried columns"
                    )

                if (stats[7] or 0) > (stats[6] or 0) * 5:  # High update rate
                    analysis['recommendations'].append(
                        "High update rate detected - consider fill factor optimization"
                    )

    except Exception as e:
        logger.error(f"Table performance analysis failed: {str(e)}")
        analysis['error'] = str(e)

    return analysis