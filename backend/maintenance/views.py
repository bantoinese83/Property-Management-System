import django_filters
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer


class MaintenanceRequestFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name="property", lookup_expr="exact")
    tenant_id = django_filters.NumberFilter(field_name="tenant", lookup_expr="exact")

    class Meta:
        model = MaintenanceRequest
        fields = ["priority", "status", "property", "category", "tenant_id"]


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing maintenance requests.

    GET /api/maintenance/ - List maintenance requests
    POST /api/maintenance/ - Create maintenance request
    GET /api/maintenance/{id}/ - Get request details
    PATCH /api/maintenance/{id}/ - Update request status
    GET /api/maintenance/overdue/ - Get overdue requests
    GET /api/maintenance/by_priority/{priority}/ - Get requests by priority
    """

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceRequestFilter
    search_fields = ["title", "description", "property__property_name"]
    ordering_fields = ["requested_date", "priority", "status"]
    ordering = ["-requested_date"]

    def get_queryset(self):
        """Filter maintenance requests by user permissions"""
        user = self.request.user

        if user.user_type == "admin":
            return MaintenanceRequest.objects.all()
        elif user.user_type in ["owner", "manager"]:
            # Property owners/managers can see requests for their properties
            return MaintenanceRequest.objects.filter(property__owner=user)
        elif user.user_type == "tenant":
            # Tenants can only see their own requests
            return MaintenanceRequest.objects.filter(tenant__id=user.id)
        else:
            return MaintenanceRequest.objects.none()

    def perform_create(self, serializer):
        """Set tenant to current user if they're a tenant"""
        data = {}
        if self.request.user.user_type == "tenant":
            data["tenant"] = self.request.user.id
        serializer.save(**data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue maintenance requests"""
        overdue_requests = self.get_queryset().filter(
            scheduled_date__lt=timezone.now(), status__in=["open", "assigned", "in_progress"]
        )
        serializer = self.get_serializer(overdue_requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"by_priority/(?P<priority>\w+)")
    def by_priority(self, request, priority=None):
        """Get maintenance requests by priority"""
        if priority not in ["low", "medium", "high", "urgent"]:
            return Response(
                {"error": "Invalid priority. Must be: low, medium, high, urgent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        requests = self.get_queryset().filter(priority=priority)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign maintenance request to a user"""
        maintenance_request = self.get_object()

        # Check if user can assign
        if maintenance_request.property.owner != request.user and request.user.user_type != "admin":
            return Response(
                {"error": "You do not have permission to assign this request"},
                status=status.HTTP_403_FORBIDDEN,
            )

        assigned_to_id = request.data.get("assigned_to")
        if not assigned_to_id:
            return Response({"error": "assigned_to field is required"}, status=status.HTTP_400_BAD_REQUEST)

        from users.models import User

        try:
            assigned_user = User.objects.get(id=assigned_to_id)
            maintenance_request.assigned_to = assigned_user
            maintenance_request.status = "assigned"
            maintenance_request.save()

            serializer = self.get_serializer(maintenance_request)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Assigned user not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark maintenance request as completed"""
        maintenance_request = self.get_object()

        # Check permissions
        if (
            maintenance_request.property.owner != request.user
            and maintenance_request.assigned_to != request.user
            and request.user.user_type != "admin"
        ):
            return Response(
                {"error": "You do not have permission to complete this request"},
                status=status.HTTP_403_FORBIDDEN,
            )

        actual_cost = request.data.get("actual_cost")
        notes = request.data.get("completion_notes")

        maintenance_request.status = "completed"
        maintenance_request.completed_date = timezone.now()
        if actual_cost is not None:
            maintenance_request.actual_cost = actual_cost
        if notes:
            maintenance_request.notes = notes

        maintenance_request.save()

        serializer = self.get_serializer(maintenance_request)
        return Response(serializer.data)
