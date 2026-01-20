from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Tenant
from .serializers import TenantSerializer
from leases.serializers import LeaseSerializer
from core.permissions import IsOwnerOrPropertyManager

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants.

    GET /api/tenants/ - List all tenants
    POST /api/tenants/ - Create new tenant
    GET /api/tenants/{id}/ - Get tenant details
    PUT /api/tenants/{id}/ - Update tenant
    DELETE /api/tenants/{id}/ - Delete tenant
    GET /api/tenants/{id}/active_leases/ - Get tenant's active leases
    """

    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'city', 'state']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'last_name', 'first_name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter tenants based on user permissions"""
        user = self.request.user

        if user.user_type == 'admin':
            return Tenant.objects.all()
        elif user.user_type in ['owner', 'manager']:
            # Owners/managers can see tenants of their properties
            return Tenant.objects.filter(
                leases__property__owner=user
            ).distinct()
        else:
            return Tenant.objects.none()

    @action(detail=True, methods=['get'])
    def active_leases(self, request, pk=None):
        """Get all active leases for a tenant"""
        tenant = self.get_object()

        from leases.models import Lease
        from django.utils import timezone

        today = timezone.now().date()
        active_leases = Lease.objects.filter(
            tenant=tenant,
            status='active',
            lease_start_date__lte=today,
            lease_end_date__gte=today
        ).select_related('property')

        serializer = LeaseSerializer(active_leases, many=True)
        return Response(serializer.data)