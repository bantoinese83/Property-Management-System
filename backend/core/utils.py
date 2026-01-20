"""
Core utility functions and mixins for the Property Management System.

This module provides reusable utilities, mixins, and helper functions
that promote code consistency, reduce duplication, and improve maintainability
across all Django applications in the PMS.

Contents:
    - CachedQuerySet: Database query caching utilities
    - ValidationUtils: Data validation helpers
    - QueryUtils: Complex database query builders
    - FinancialUtils: Financial calculation utilities
    - AuditUtils: Audit logging helpers
    - SerializerUtils: DRF serializer utilities
    - ViewSetUtils: DRF ViewSet helpers
    - PermissionUtils: Permission checking utilities
    - BaseViewSet: Enhanced ViewSet with mixins
    - ReadOnlyBaseViewSet: Read-only ViewSet with mixins

Usage:
    from core.utils import FinancialUtils, AuditUtils
    from core.mixins import BaseViewSet

    # Calculate occupancy rate
    rate = FinancialUtils.calculate_occupancy_rate(property_obj)

    # Log an audit event
    AuditUtils.log_model_change(user, instance, 'update')

    # Create a ViewSet with built-in features
    class MyViewSet(BaseViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MySerializer
"""

from typing import Any, Dict, List, Optional, Type, Union

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.request import Request
from rest_framework.response import Response


class CachedQuerySet:
    """Mixin for caching queryset results."""

    @staticmethod
    def get_cached_queryset(
        queryset: QuerySet,
        cache_key: str,
        timeout: int = 300,
        force_refresh: bool = False
    ) -> QuerySet:
        """
        Get queryset from cache or execute and cache it.

        Args:
            queryset: The queryset to cache
            cache_key: Unique cache key
            timeout: Cache timeout in seconds (default: 5 minutes)
            force_refresh: Force cache refresh

        Returns:
            Cached queryset results
        """
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        # Execute queryset and cache results
        result = list(queryset)  # Evaluate queryset
        cache.set(cache_key, result, timeout)
        return result


class ValidationUtils:
    """Utility functions for data validation."""

    @staticmethod
    def validate_date_range(
        start_date: Optional[timezone.datetime.date],
        end_date: Optional[timezone.datetime.date],
        field_name: str = "date range"
    ) -> None:
        """
        Validate that start_date is before end_date.

        Args:
            start_date: Start date
            end_date: End date
            field_name: Field name for error messages

        Raises:
            ValidationError: If validation fails
        """
        if start_date and end_date and start_date >= end_date:
            raise ValidationError(
                f"{field_name.title()}: Start date must be before end date."
            )

    @staticmethod
    def validate_positive_amount(
        amount: Union[int, float, str],
        field_name: str = "amount"
    ) -> None:
        """
        Validate that amount is positive.

        Args:
            amount: Amount to validate
            field_name: Field name for error messages

        Raises:
            ValidationError: If validation fails
        """
        try:
            numeric_amount = float(amount)
            if numeric_amount <= 0:
                raise ValidationError(
                    f"{field_name.title()}: Amount must be positive."
                )
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name.title()}: Invalid amount format."
            )


class QueryUtils:
    """Utility functions for complex database queries."""

    @staticmethod
    def get_active_leases_for_property(property_id: int) -> QuerySet:
        """Get all active leases for a property."""
        from leases.models import Lease

        today = timezone.now().date()
        return Lease.objects.filter(
            property_obj_id=property_id,
            lease_start_date__lte=today,
            lease_end_date__gte=today,
            status="active"
        )

    @staticmethod
    def get_overdue_payments_for_property(property_id: int) -> QuerySet:
        """Get overdue payments for a property."""
        from payments.models import RentPayment

        today = timezone.now().date()
        return RentPayment.objects.filter(
            lease_obj__property_obj_id=property_id,
            due_date__lt=today,
            status__in=["pending", "overdue"]
        )

    @staticmethod
    def get_upcoming_maintenance_for_property(property_id: int, days_ahead: int = 30) -> QuerySet:
        """Get upcoming maintenance requests for a property."""
        from maintenance.models import MaintenanceRequest
        from django.utils import timezone

        future_date = timezone.now().date() + timezone.timedelta(days=days_ahead)
        return MaintenanceRequest.objects.filter(
            property_id=property_id,
            scheduled_date__lte=future_date,
            scheduled_date__gte=timezone.now().date(),
            status__in=["scheduled", "pending"]
        )


class FinancialUtils:
    """Utility functions for financial calculations."""

    @staticmethod
    def calculate_occupancy_rate(property_obj) -> float:
        """Calculate occupancy rate for a property."""
        from leases.models import Lease

        today = timezone.now().date()
        active_leases = Lease.objects.filter(
            property_obj=property_obj,
            lease_start_date__lte=today,
            lease_end_date__gte=today,
            status="active"
        ).count()

        if property_obj.total_units == 0:
            return 0.0

        return round((active_leases / property_obj.total_units) * 100, 2)

    @staticmethod
    def calculate_monthly_income(property_obj) -> float:
        """Calculate expected monthly income for a property."""
        from leases.models import Lease

        today = timezone.now().date()
        total_rent = Lease.objects.filter(
            property_obj=property_obj,
            lease_start_date__lte=today,
            lease_end_date__gte=today,
            status="active"
        ).aggregate(total=models.Sum("monthly_rent"))["total"]

        return float(total_rent or 0)

    @staticmethod
    def calculate_property_profit_margin(property_obj, period_start: timezone.datetime.date, period_end: timezone.datetime.date) -> float:
        """Calculate profit margin for a property over a date range."""
        from accounting.models import FinancialTransaction

        income = FinancialTransaction.objects.filter(
            property_obj=property_obj,
            transaction_type="income",
            transaction_date__gte=period_start,
            transaction_date__lte=period_end
        ).aggregate(total=models.Sum("amount"))["total"] or 0

        expenses = FinancialTransaction.objects.filter(
            property_obj=property_obj,
            transaction_type="expense",
            transaction_date__gte=period_start,
            transaction_date__lte=period_end
        ).aggregate(total=models.Sum("amount"))["total"] or 0

        if income == 0:
            return 0.0

        net_income = income - expenses
        return round((net_income / income) * 100, 2)


class AuditUtils:
    """Utility functions for audit logging."""

    @staticmethod
    def log_model_change(
        user: models.Model,
        instance: models.Model,
        action: str,
        changes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a model change to the audit system.

        Args:
            user: User performing the action
            instance: Model instance being changed
            action: Action performed (create, update, delete)
            changes: Dictionary of field changes
        """
        from audit.models import AuditLog

        try:
            AuditLog.objects.create(
                user=user,
                content_object=instance,
                action=action,
                action_description=f"{action.title()} {instance._meta.model_name}",
                old_values=changes.get("old") if changes else None,
                new_values=changes.get("new") if changes else None,
                app_label=instance._meta.app_label,
                model_name=instance._meta.model_name,
                username=user.username if hasattr(user, "username") else str(user)
            )
        except Exception:
            # Don't let audit logging break the main operation
            pass

    @staticmethod
    def get_recent_activity(user: models.Model, limit: int = 10) -> QuerySet:
        """Get recent activity for a user."""
        from audit.models import AuditLog

        return AuditLog.objects.filter(user=user).order_by("-timestamp")[:limit]


class SerializerUtils:
    """Utility functions for DRF serializers."""

    @staticmethod
    def create_nested_serializer(
        model_class: Type[models.Model],
        serializer_class: Type[serializers.ModelSerializer],
        many: bool = False,
        **kwargs
    ) -> serializers.ModelSerializer:
        """
        Create a nested serializer with proper validation.

        Args:
            model_class: The model class
            serializer_class: The serializer class
            many: Whether this is a many relationship
            **kwargs: Additional serializer kwargs

        Returns:
            Configured serializer instance
        """
        return serializer_class(many=many, **kwargs)

    @staticmethod
    def validate_nested_data(data: Dict[str, Any], serializer_class: Type[serializers.ModelSerializer]) -> Dict[str, Any]:
        """
        Validate nested data using a serializer.

        Args:
            data: Data to validate
            serializer_class: Serializer class to use

        Returns:
            Validated data

        Raises:
            ValidationError: If validation fails
        """
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class ViewSetUtils:
    """Utility functions for DRF viewsets."""

    @staticmethod
    def get_filtered_queryset(
        viewset: viewsets.ModelViewSet,
        queryset: QuerySet,
        request: Request
    ) -> QuerySet:
        """
        Apply standard filtering, searching, and ordering to a queryset.

        Args:
            viewset: The viewset instance
            queryset: Base queryset
            request: Request object

        Returns:
            Filtered queryset
        """
        # Apply filtering
        if hasattr(viewset, 'filter_backends'):
            for backend in viewset.filter_backends:
                queryset = backend().filter_queryset(request, queryset, viewset)

        return queryset

    @staticmethod
    def paginated_response(
        viewset: viewsets.ModelViewSet,
        queryset: QuerySet,
        serializer_class: Type[serializers.ModelSerializer],
        request: Request
    ) -> Response:
        """
        Create a paginated response from a queryset.

        Args:
            viewset: The viewset instance
            queryset: Queryset to paginate
            serializer_class: Serializer class
            request: Request object

        Returns:
            Paginated response
        """
        page = viewset.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True, context={'request': request})
            return viewset.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class PermissionUtils:
    """Utility functions for permission checking."""

    @staticmethod
    def is_property_owner(user: models.Model, property_obj: models.Model) -> bool:
        """Check if user owns the property."""
        return hasattr(property_obj, 'owner') and property_obj.owner == user

    @staticmethod
    def is_property_manager(user: models.Model, property_obj: models.Model) -> bool:
        """Check if user is a manager of the property."""
        return user.user_type in ['admin', 'manager'] or PermissionUtils.is_property_owner(user, property_obj)

    @staticmethod
    def can_access_tenant_data(user: models.Model, tenant: models.Model) -> bool:
        """Check if user can access tenant data."""
        if user.user_type == 'admin':
            return True

        # Check if user manages any properties that this tenant has leases for
        from leases.models import Lease
        return Lease.objects.filter(
            tenant=tenant,
            property_obj__owner=user
        ).exists()

    @staticmethod
    def filter_queryset_by_permissions(user: models.Model, queryset: QuerySet, model_name: str) -> QuerySet:
        """
        Filter queryset based on user permissions.

        Args:
            user: User instance
            queryset: Base queryset
            model_name: Name of the model being filtered

        Returns:
            Filtered queryset
        """
        if user.user_type == 'admin':
            return queryset

        if model_name == 'property':
            return queryset.filter(owner=user)
        elif model_name in ['lease', 'payment', 'maintenance']:
            # Filter by properties the user owns
            return queryset.filter(property_obj__owner=user)
        elif model_name == 'tenant':
            # Filter tenants that have leases on user's properties
            return queryset.filter(
                leases__property_obj__owner=user
            ).distinct()

        return queryset.none()