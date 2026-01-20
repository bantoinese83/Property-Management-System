from django.utils import timezone
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RentPayment
from .serializers import RentPaymentSerializer


class RentPaymentFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name='lease_obj__property', lookup_expr='exact')

    class Meta:
        model = RentPayment
        fields = ['status', 'payment_method', 'property']


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
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RentPaymentFilter
    search_fields = ["lease_obj__tenant__first_name", "lease_obj__tenant__last_name"]
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
        is_owner = payment.lease.property.owner == request.user
        is_admin = request.user.user_type == "admin"
        if not is_owner and not is_admin:
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

        total_collected = sum(
            p.amount for p in payments if p.status == "paid"
        )
        total_pending = sum(
            p.amount for p in payments if p.status == "pending"
        )
        total_overdue = sum(
            p.amount for p in payments if p.status == "overdue"
        )

        return Response(
            {
                "month": month_start.strftime("%Y-%m"),
                "total_collected": str(total_collected),
                "total_pending": str(total_pending),
                "total_overdue": str(total_overdue),
                "total_payments": payments.count(),
            }
        )

    @action(detail=True, methods=["post"])
    def create_checkout_session(self, request, pk=None):
        """Create a Stripe checkout session for a payment"""
        payment = self.get_object()

        if payment.status == "paid":
            return Response(
                {"error": "This payment has already been completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            import stripe
            from django.conf import settings

            stripe.api_key = settings.STRIPE_SECRET_KEY

            # success_url and cancel_url should ideally come from
            # frontend or settings. Using defaults for local development
            success_url = request.data.get(
                "success_url",
                (
                    "http://localhost:5173/payments?success=true"
                    "&session_id={CHECKOUT_SESSION_ID}"
                ),
            )
            cancel_url = request.data.get(
                "cancel_url",
                "http://localhost:5173/payments?canceled=true",
            )

            prop_name = payment.lease_obj.property.property_name
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Rent Payment - {prop_name}",
                                "description": (
                                    f"Payment for "
                                    f"{payment.due_date.strftime('%B %Y')}"
                                ),
                            },
                            "unit_amount": int(
                                payment.total_amount * 100
                            ),  # Amount in cents
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(payment.id),
                metadata={
                    "payment_id": str(payment.id),
                },
            )

            return Response({"url": checkout_session.url})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
