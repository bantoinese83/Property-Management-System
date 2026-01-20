from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RentPayment
from .serializers import RentPaymentSerializer


class RentPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rent payments.

    GET /api/payments/ - List payments (filtered by permissions)
    POST /api/payments/ - Record new payment
    GET /api/payments/{id}/ - Get payment details
    PATCH /api/payments/{id}/ - Update payment status
    GET /api/payments/overdue/ - Get overdue payments
    GET /api/payments/pending/ - Get pending payments
    POST /api/payments/{id}/mark_paid/ - Mark payment as paid
    """

    serializer_class = RentPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "payment_method", "lease__property"]
    search_fields = ["lease__tenant__first_name", "lease__tenant__last_name"]
    ordering_fields = ["payment_date", "due_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        """Filter payments by user permissions"""
        user = self.request.user

        if user.user_type == "admin":
            return RentPayment.objects.all()
        elif user.user_type in ["owner", "manager"]:
            # Property owners/managers can see payments for their properties
            return RentPayment.objects.filter(lease__property__owner=user)
        elif user.user_type == "tenant":
            # Tenants can only see their own payments
            return RentPayment.objects.filter(lease__tenant__id=user.id)
        else:
            return RentPayment.objects.none()

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue payments"""
        today = timezone.now().date()
        overdue_payments = self.get_queryset().filter(
            due_date__lt=today, status__in=["pending", "overdue"]
        )
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending payments"""
        pending_payments = self.get_queryset().filter(status="pending")
        serializer = self.get_serializer(pending_payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark a payment as paid"""
        payment = self.get_object()

        # Check permissions
        if payment.lease.property.owner != request.user and request.user.user_type != "admin":
            return Response(
                {"error": "You do not have permission to update this payment"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update payment status
        payment.status = "paid"
        payment.processed_by = request.user
        payment.processed_at = timezone.now()

        # Optional fields from request
        transaction_id = request.data.get("transaction_id")
        payment_processor = request.data.get("payment_processor")
        notes = request.data.get("notes")

        if transaction_id:
            payment.transaction_id = transaction_id
        if payment_processor:
            payment.payment_processor = payment_processor
        if notes:
            payment.notes = notes

        payment.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def monthly_summary(self, request):
        """Get monthly payment summary"""
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Get payments for current month
        payments = self.get_queryset().filter(
            payment_date__gte=month_start, payment_date__lte=today
        )

        total_collected = sum(p.amount for p in payments if p.status == "paid")
        total_pending = sum(p.amount for p in payments if p.status == "pending")
        total_overdue = sum(p.amount for p in payments if p.status == "overdue")

        return Response(
            {
                "month": month_start.strftime("%Y-%m"),
                "total_collected": str(total_collected),
                "total_pending": str(total_pending),
                "total_overdue": str(total_overdue),
                "total_payments": payments.count(),
            }
        )
