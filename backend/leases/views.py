from django.utils import timezone
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import Lease
from .serializers import LeaseSerializer


class LeaseFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name='property_obj', lookup_expr='exact')
    tenant_id = django_filters.NumberFilter(field_name='tenant', lookup_expr='exact')

    class Meta:
        model = Lease
        fields = ['status', 'property', 'tenant_id']


class LeaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leases.

    GET /api/leases/ - List all leases (filtered by permissions)
    POST /api/leases/ - Create new lease
    GET /api/leases/{id}/ - Get lease details
    PUT /api/leases/{id}/ - Update lease
    DELETE /api/leases/{id}/ - Delete lease
    GET /api/leases/expiring_soon/ - Get leases expiring soon
    POST /api/leases/{id}/renew/ - Renew a lease
    """

    serializer_class = LeaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaseFilter
    search_fields = ["tenant__first_name", "tenant__last_name", "property_obj__property_name"]
    ordering_fields = ["lease_start_date", "lease_end_date", "created_at"]
    ordering = ["-lease_start_date"]

    def get_queryset(self):
        """Filter leases by user permissions"""
        user = self.request.user

        if user.user_type == "admin":
            return Lease.objects.all()
        elif user.user_type in ["owner", "manager"]:
            return Lease.objects.filter(property_obj__owner=user)
        else:
            return Lease.objects.none()

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """Get leases expiring within next 30 days"""
        today = timezone.now().date()
        leases = self.get_queryset().filter(
            lease_end_date__gte=today,
            lease_end_date__lte=today + timezone.timedelta(days=30),
            status__in=["active", "pending"],
        )
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        """Renew a lease"""
        lease = self.get_object()

        # Check permissions
        if lease.property_obj.owner != request.user and request.user.user_type != "admin":
            return Response(
                {"error": "You do not have permission to renew this lease"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get renewal data from request
        renewal_months = request.data.get("renewal_months", 12)
        new_rent = request.data.get("new_rent")

        # Calculate new dates
        new_end_date = lease.lease_end_date + timezone.timedelta(days=30 * renewal_months)

        # Update lease
        lease.lease_end_date = new_end_date
        if new_rent:
            lease.monthly_rent = new_rent
        lease.status = "active"
        lease.save()

        serializer = self.get_serializer(lease)
        return Response(serializer.data)
