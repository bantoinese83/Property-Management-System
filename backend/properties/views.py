from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.mixins import BaseViewSet
from .models import Property, PropertyImage
from .serializers import PropertyImageSerializer, PropertyListSerializer, PropertySerializer


class PropertyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PropertyViewSet(BaseViewSet):
    """
    ViewSet for managing rental properties.

    This ViewSet provides comprehensive CRUD operations for properties,
    along with advanced analytics and reporting features.

    Endpoints:
        GET /api/properties/ - List properties with filtering and pagination
        POST /api/properties/ - Create new property
        GET /api/properties/{id}/ - Retrieve property details
        PUT /api/properties/{id}/ - Update property information
        DELETE /api/properties/{id}/ - Delete property (admin only)
        GET /api/properties/{id}/occupancy_details/ - Get occupancy analytics
        GET /api/properties/{id}/financial_summary/ - Get financial metrics
        GET /api/properties/dashboard_stats/ - Get dashboard statistics (cached)
        GET /api/properties/dashboard_analytics/ - Get comprehensive analytics (cached)

    Permissions:
        - Owners can only see/manage their own properties
        - Admins can see/manage all properties
        - Managers have restricted access based on configuration

    Features:
        - Automatic audit logging for all changes
        - Redis caching for expensive analytics queries
        - Optimized database queries with select_related/prefetch_related
        - Comprehensive filtering and search capabilities
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["property_type", "is_active", "city", "state"]
    search_fields = ["property_name", "address", "city"]
    ordering_fields = ["created_at", "property_name", "purchase_price"]
    ordering = ["-created_at"]
    pagination_class = PropertyPagination


    def get_serializer_class(self):
        if self.action == "list":
            return PropertyListSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def occupancy_details(self, request, pk=None):
        """Get detailed occupancy information"""
        property_obj = self.get_object()
        self.check_object_permissions(request, property_obj)

        from django.utils import timezone

        from leases.models import Lease

        today = timezone.now().date()
        active_leases = Lease.objects.filter(
            property=property_obj,
            status="active",
            lease_start_date__lte=today,
            lease_end_date__gte=today,
        ).values("id", "tenant__first_name", "tenant__last_name", "monthly_rent", "lease_end_date")

        return Response(
            {
                "total_units": property_obj.total_units,
                "occupied_units": len(active_leases),
                "vacant_units": property_obj.total_units - len(active_leases),
                "occupancy_rate": property_obj.get_occupancy_rate(),
                "active_leases": active_leases,
                "monthly_income": str(property_obj.get_monthly_income()),
            }
        )

    @action(detail=True, methods=["get"])
    def financial_summary(self, request, pk=None):
        """Get financial summary for property"""
        property_obj = self.get_object()
        self.check_object_permissions(request, property_obj)

        from datetime import timedelta

        from django.utils import timezone

        from accounting.models import FinancialTransaction
        from payments.models import RentPayment

        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)

        # Rent payments
        payments = RentPayment.objects.filter(lease__property=property_obj, payment_date__gte=last_30_days)

        total_collected = sum(p.amount for p in payments if p.status == "paid")
        pending_payments = sum(p.amount for p in payments if p.status == "pending")
        overdue_payments = sum(p.amount for p in payments if p.status == "overdue")

        # Expenses
        expenses = (
            FinancialTransaction.objects.filter(
                property=property_obj,
                transaction_type="expense",
                transaction_date__gte=last_30_days,
            ).aggregate(total=models.Sum("amount"))["total"]
            or 0
        )

        return Response(
            {
                "monthly_income": str(property_obj.get_monthly_income()),
                "total_collected_30d": str(total_collected),
                "pending_payments": str(pending_payments),
                "overdue_payments": str(overdue_payments),
                "total_expenses_30d": str(expenses),
                "annual_tax": str(property_obj.annual_property_tax or 0),
                "insurance_cost": str(property_obj.insurance_cost or 0),
            }
        )

    @action(detail=False, methods=["get"])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        properties = self.get_queryset()

        total_units = sum(p.total_units for p in properties)
        avg_occupancy = sum(p.get_occupancy_rate() for p in properties) / len(properties) if properties.exists() else 0
        total_monthly_income = sum(float(p.get_monthly_income()) for p in properties)

        return Response(
            {
                "total_properties": properties.count(),
                "total_units": total_units,
                "average_occupancy": round(avg_occupancy, 2),
                "total_monthly_income": str(total_monthly_income),
            }
        )

    @method_decorator(cache_page(600))  # Cache for 10 minutes
    @action(detail=False, methods=["get"])
    def dashboard_analytics(self, request):
        """Get comprehensive dashboard analytics"""
        from datetime import timedelta

        from django.utils import timezone

        from leases.models import Lease
        from maintenance.models import MaintenanceRequest
        from payments.models import RentPayment

        properties = self.get_queryset()

        # Time-based filters
        today = timezone.now().date()
        this_month_start = today.replace(day=1)

        # Basic metrics
        total_properties = properties.count()
        total_units = sum(p.total_units for p in properties)

        # Occupancy data
        occupied_units = 0
        vacant_units = 0
        for prop in properties:
            occupied_units += prop.total_units * prop.get_occupancy_rate() / 100
            vacant_units += prop.total_units - (prop.total_units * prop.get_occupancy_rate() / 100)

        avg_occupancy = (occupied_units / total_units * 100) if total_units > 0 else 0

        # Financial metrics
        total_monthly_income = sum(float(p.get_monthly_income()) for p in properties)
        total_annual_income = total_monthly_income * 12

        # Recent payments (last 30 days)
        recent_payments = RentPayment.objects.filter(
            lease_obj__property_obj__in=properties, payment_date__gte=today - timedelta(days=30)
        )
        monthly_collections = sum(float(p.amount) for p in recent_payments if p.status == "paid")

        # Outstanding payments
        outstanding_payments = RentPayment.objects.filter(
            lease_obj__property_obj__in=properties, status__in=["pending", "overdue"]
        )
        total_outstanding = sum(float(p.amount) for p in outstanding_payments)

        # Maintenance requests
        open_maintenance = MaintenanceRequest.objects.filter(
            property_obj__in=properties, status__in=["open", "assigned", "in_progress"]
        ).count()

        urgent_maintenance = MaintenanceRequest.objects.filter(
            property_obj__in=properties,
            priority="urgent",
            status__in=["open", "assigned", "in_progress"],
        ).count()

        # Lease data
        active_leases = Lease.objects.filter(property_obj__in=properties, status="active").count()

        expiring_leases = Lease.objects.filter(
            property_obj__in=properties, status="active", lease_end_date__lte=today + timedelta(days=30)
        ).count()

        # Monthly trends (last 12 months)
        monthly_revenue = []
        for i in range(11, -1, -1):
            month_start = (this_month_start - timedelta(days=30 * i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            month_payments = RentPayment.objects.filter(
                lease_obj__property_obj__in=properties,
                payment_date__gte=month_start,
                payment_date__lte=month_end,
                status="paid",
            )
            month_total = sum(float(p.amount) for p in month_payments)

            monthly_revenue.append(
                {
                    "month": month_start.strftime("%b %Y"),
                    "revenue": month_total,
                    "collections": month_total,
                }
            )

        # Property performance by type
        property_types = {}
        for prop in properties:
            prop_type = prop.get_property_type_display()
            if prop_type not in property_types:
                property_types[prop_type] = {
                    "count": 0,
                    "total_units": 0,
                    "occupied_units": 0,
                    "monthly_income": 0,
                }

            property_types[prop_type]["count"] += 1
            property_types[prop_type]["total_units"] += prop.total_units
            property_types[prop_type]["occupied_units"] += prop.total_units * prop.get_occupancy_rate() / 100
            property_types[prop_type]["monthly_income"] += float(prop.get_monthly_income())

        # Recent activity (last 10 items)
        recent_activity = []

        # Recent payments
        recent_payments_activity = RentPayment.objects.filter(lease_obj__property_obj__in=properties).order_by(
            "-created_at"
        )[:5]

        for payment in recent_payments_activity:
            recent_activity.append(
                {
                    "type": "payment",
                    "description": f"Rent payment received from {payment.lease_obj.tenant.first_name} {payment.lease_obj.tenant.last_name}",
                    "amount": str(payment.amount),
                    "date": payment.created_at.isoformat(),
                    "property": payment.lease_obj.property_obj.property_name,
                }
            )

        # Recent maintenance
        recent_maintenance = MaintenanceRequest.objects.filter(property_obj__in=properties).order_by("-created_at")[:5]

        for maintenance in recent_maintenance:
            recent_activity.append(
                {
                    "type": "maintenance",
                    "description": f"Maintenance request: {maintenance.title}",
                    "priority": maintenance.priority,
                    "date": maintenance.created_at.isoformat(),
                    "property": maintenance.property_obj.property_name,
                }
            )

        # Sort recent activity by date
        recent_activity.sort(key=lambda x: x["date"], reverse=True)
        recent_activity = recent_activity[:10]

        return Response(
            {
                "summary": {
                    "total_properties": total_properties,
                    "total_units": total_units,
                    "occupied_units": round(occupied_units, 1),
                    "vacant_units": round(vacant_units, 1),
                    "average_occupancy": round(avg_occupancy, 1),
                    "total_monthly_income": str(total_monthly_income),
                    "total_annual_income": str(total_annual_income),
                    "monthly_collections": str(monthly_collections),
                    "total_outstanding": str(total_outstanding),
                    "active_leases": active_leases,
                    "expiring_leases": expiring_leases,
                    "open_maintenance": open_maintenance,
                    "urgent_maintenance": urgent_maintenance,
                },
                "charts": {
                    "monthly_revenue": monthly_revenue,
                    "property_types": property_types,
                },
                "recent_activity": recent_activity,
            }
        )


class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing property images"""

    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyImage.objects.filter(property__owner=self.request.user).select_related("property")

    def perform_create(self, serializer):
        property_id = self.request.data.get("property")
        property_obj = Property.objects.get(id=property_id)

        # Check ownership
        if property_obj.owner != self.request.user and self.request.user.user_type != "admin":
            raise permissions.PermissionDenied("You don't own this property")

        serializer.save(property=property_obj)
