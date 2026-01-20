from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Property, PropertyImage
from .serializers import PropertySerializer, PropertyListSerializer, PropertyImageSerializer
from core.permissions import IsPropertyOwnerOrReadOnly, IsOwnerOrPropertyManager

class PropertyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing properties.

    GET /api/properties/ - List all properties (filtered by owner)
    POST /api/properties/ - Create new property
    GET /api/properties/{id}/ - Get property details
    PUT /api/properties/{id}/ - Update property
    DELETE /api/properties/{id}/ - Delete property
    GET /api/properties/{id}/occupancy_details/ - Get occupancy info
    GET /api/properties/{id}/financial_summary/ - Get financial stats
    GET /api/properties/dashboard_stats/ - Get dashboard statistics
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['property_type', 'is_active', 'city', 'state']
    search_fields = ['property_name', 'address', 'city']
    ordering_fields = ['created_at', 'property_name', 'purchase_price']
    ordering = ['-created_at']
    pagination_class = PropertyPagination

    def get_queryset(self):
        """Filter properties by user role"""
        user = self.request.user

        if user.user_type == 'admin':
            return Property.objects.all()
        elif user.user_type in ['owner', 'manager']:
            return Property.objects.filter(owner=user)
        else:
            return Property.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        """Set owner to current user"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def occupancy_details(self, request, pk=None):
        """Get detailed occupancy information"""
        property_obj = self.get_object()
        self.check_object_permissions(request, property_obj)

        from leases.models import Lease
        from django.utils import timezone

        today = timezone.now().date()
        active_leases = Lease.objects.filter(
            property=property_obj,
            status='active',
            lease_start_date__lte=today,
            lease_end_date__gte=today
        ).values(
            'id', 'tenant__first_name', 'tenant__last_name',
            'monthly_rent', 'lease_end_date'
        )

        return Response({
            'total_units': property_obj.total_units,
            'occupied_units': len(active_leases),
            'vacant_units': property_obj.total_units - len(active_leases),
            'occupancy_rate': property_obj.get_occupancy_rate(),
            'active_leases': active_leases,
            'monthly_income': str(property_obj.get_monthly_income()),
        })

    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """Get financial summary for property"""
        property_obj = self.get_object()
        self.check_object_permissions(request, property_obj)

        from payments.models import RentPayment
        from accounting.models import FinancialTransaction
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)

        # Rent payments
        payments = RentPayment.objects.filter(
            lease__property=property_obj,
            payment_date__gte=last_30_days
        )

        total_collected = sum(
            p.amount for p in payments if p.status == 'paid'
        )
        pending_payments = sum(
            p.amount for p in payments if p.status == 'pending'
        )
        overdue_payments = sum(
            p.amount for p in payments if p.status == 'overdue'
        )

        # Expenses
        expenses = FinancialTransaction.objects.filter(
            property=property_obj,
            transaction_type='expense',
            transaction_date__gte=last_30_days
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        return Response({
            'monthly_income': str(property_obj.get_monthly_income()),
            'total_collected_30d': str(total_collected),
            'pending_payments': str(pending_payments),
            'overdue_payments': str(overdue_payments),
            'total_expenses_30d': str(expenses),
            'annual_tax': str(property_obj.annual_property_tax or 0),
            'insurance_cost': str(property_obj.insurance_cost or 0),
        })

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        properties = self.get_queryset()

        total_units = sum(p.total_units for p in properties)
        avg_occupancy = (
            sum(p.get_occupancy_rate() for p in properties) / len(properties)
            if properties.exists() else 0
        )
        total_monthly_income = sum(
            float(p.get_monthly_income()) for p in properties
        )

        return Response({
            'total_properties': properties.count(),
            'total_units': total_units,
            'average_occupancy': round(avg_occupancy, 2),
            'total_monthly_income': str(total_monthly_income),
        })

class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing property images"""

    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PropertyImage.objects.filter(
            property__owner=self.request.user
        ).select_related('property')

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        property_obj = Property.objects.get(id=property_id)

        # Check ownership
        if property_obj.owner != self.request.user and self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("You don't own this property")

        serializer.save(property=property_obj)