"""
Base mixins for Django REST Framework viewsets.

This module provides reusable mixins that add common functionality
to DRF viewsets across the application.
"""

from typing import Any, Dict, List, Optional, Type

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .utils import PermissionUtils, ViewSetUtils


class CachedViewSetMixin:
    """
    Mixin that adds caching capabilities to viewsets.

    Provides methods for caching queryset results and API responses.
    """

    cache_timeout: int = 300  # 5 minutes default

    def get_cache_key(self, request: Request, action: str = "") -> str:
        """
        Generate a cache key for the current request.

        Args:
            request: The request object
            action: Optional action name

        Returns:
            Cache key string
        """
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        path = request.get_full_path()
        return f"viewset:{self.__class__.__name__}:{action}:{user_id}:{path}"

    def get_cached_response(self, request: Request, cache_key: str) -> Optional[Response]:
        """
        Get cached response if available.

        Args:
            request: The request object
            cache_key: Cache key

        Returns:
            Cached response or None
        """
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        return None

    def cache_response(self, response: Response, cache_key: str, timeout: Optional[int] = None) -> Response:
        """
        Cache a response.

        Args:
            response: Response to cache
            cache_key: Cache key
            timeout: Cache timeout (uses self.cache_timeout if not provided)

        Returns:
            The response (unchanged)
        """
        timeout = timeout or self.cache_timeout
        cache.set(cache_key, response.data, timeout)
        return response


class PermissionViewSetMixin:
    """
    Mixin that adds enhanced permission checking to viewsets.

    Provides role-based filtering and permission validation.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Get queryset filtered by user permissions.

        Returns:
            Filtered queryset based on user role
        """
        queryset = super().get_queryset()
        model_name = self.queryset.model._meta.model_name

        return PermissionUtils.filter_queryset_by_permissions(
            self.request.user, queryset, model_name
        )

    def perform_create(self, serializer: serializers.ModelSerializer) -> None:
        """Set the user field on create operations."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer: serializers.ModelSerializer) -> None:
        """Set the updated_by field on update operations."""
        serializer.save(updated_by=self.request.user)


class AuditViewSetMixin:
    """
    Mixin that adds audit logging to viewsets.

    Automatically logs create, update, and delete operations.
    """

    def perform_create(self, serializer: serializers.ModelSerializer) -> None:
        """Create instance and log the action."""
        instance = serializer.save()

        # Log the creation
        from .utils import AuditUtils
        AuditUtils.log_model_change(
            user=self.request.user,
            instance=instance,
            action="create"
        )

        return instance

    def perform_update(self, serializer: serializers.ModelSerializer) -> None:
        """Update instance and log the changes."""
        instance = self.get_object()
        old_values = self._get_instance_data(instance)

        updated_instance = serializer.save()

        # Get new values for comparison
        new_values = self._get_instance_data(updated_instance)
        changes = {"old": old_values, "new": new_values}

        # Log the update
        from .utils import AuditUtils
        AuditUtils.log_model_change(
            user=self.request.user,
            instance=updated_instance,
            action="update",
            changes=changes
        )

        return updated_instance

    def perform_destroy(self, instance) -> None:
        """Delete instance and log the action."""
        # Log the deletion before deleting
        from .utils import AuditUtils
        AuditUtils.log_model_change(
            user=self.request.user,
            instance=instance,
            action="delete"
        )

        super().perform_destroy(instance)

    def _get_instance_data(self, instance) -> Dict[str, Any]:
        """Get serializable data from model instance."""
        # Get fields that should be tracked for changes
        tracked_fields = getattr(self, 'audit_fields', None)
        if tracked_fields:
            return {field: getattr(instance, field) for field in tracked_fields}

        # Default: track all non-relational fields
        data = {}
        for field in instance._meta.get_fields():
            if not field.is_relation and hasattr(instance, field.name):
                value = getattr(instance, field.name)
                # Convert model instances to IDs for serialization
                if hasattr(value, 'id'):
                    value = value.id
                data[field.name] = value
        return data


class OptimizedViewSetMixin:
    """
    Mixin that adds performance optimizations to viewsets.

    Includes query optimization, select_related/prefetch_related, and pagination.
    """

    # Fields to select_related (override in subclasses)
    select_related_fields: List[str] = []

    # Fields to prefetch_related (override in subclasses)
    prefetch_related_fields: List[str] = []

    def get_queryset(self) -> QuerySet:
        """
        Get optimized queryset with select_related and prefetch_related.

        Returns:
            Optimized queryset
        """
        queryset = super().get_queryset()

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)

        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        return queryset


class BaseViewSet(
    CachedViewSetMixin,
    PermissionViewSetMixin,
    AuditViewSetMixin,
    OptimizedViewSetMixin,
    viewsets.ModelViewSet
):
    """
    Base viewset that combines all mixins.

    Provides:
    - Caching capabilities
    - Permission-based filtering
    - Automatic audit logging
    - Query optimization
    - Standard CRUD operations
    """

    pass


class ReadOnlyBaseViewSet(
    CachedViewSetMixin,
    PermissionViewSetMixin,
    OptimizedViewSetMixin,
    viewsets.ReadOnlyModelViewSet
):
    """
    Base read-only viewset with caching and permissions.

    Provides:
    - Caching capabilities
    - Permission-based filtering
    - Query optimization
    - Read-only operations
    """

    pass