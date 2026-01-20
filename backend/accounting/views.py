from django.db.models import Sum
from django.utils import timezone
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AccountingPeriod, FinancialTransaction
from .serializers import AccountingPeriodSerializer, FinancialTransactionSerializer


class FinancialTransactionFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name='property_obj', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='transaction_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='transaction_date', lookup_expr='lte')

    class Meta:
        model = FinancialTransaction
        fields = ['transaction_type', 'category', 'property']


class FinancialTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial transactions.

    GET /api/accounting/transactions/ - List transactions
    POST /api/accounting/transactions/ - Create transaction
    GET /api/accounting/transactions/{id}/ - Get transaction details
    PUT /api/accounting/transactions/{id}/ - Update transaction
    DELETE /api/accounting/transactions/{id}/ - Delete transaction
    GET /api/accounting/transactions/summary/ - Get financial summary
    """

    serializer_class = FinancialTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FinancialTransactionFilter
    search_fields = ["description", "vendor_name"]
    ordering_fields = ["transaction_date", "amount"]
    ordering = ["-transaction_date"]

    def get_queryset(self):
        """Filter transactions by user permissions"""
        user = self.request.user

        if user.user_type == "admin":
            return FinancialTransaction.objects.all()
        elif user.user_type in ["owner", "manager"]:
            return FinancialTransaction.objects.filter(property_obj__owner=user)
        else:
            return FinancialTransaction.objects.none()

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get financial summary for properties"""
        today = timezone.now().date()

        # Date range filter (default to current month)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date:
            start_date = today.replace(day=1)
        else:
            start_date = timezone.datetime.fromisoformat(start_date).date()

        if not end_date:
            end_date = today
        else:
            end_date = timezone.datetime.fromisoformat(end_date).date()

        # Filter transactions by user permissions and date range
        transactions = self.get_queryset().filter(
            transaction_date__gte=start_date, transaction_date__lte=end_date
        )

        # Calculate totals
        income_total = (
            transactions.filter(transaction_type="income").aggregate(total=Sum("amount"))["total"]
            or 0
        )

        expense_total = (
            transactions.filter(transaction_type="expense").aggregate(total=Sum("amount"))["total"]
            or 0
        )

        net_income = income_total - expense_total

        # Category breakdown
        income_by_category = (
            transactions.filter(transaction_type="income")
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        expense_by_category = (
            transactions.filter(transaction_type="expense")
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        return Response(
            {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                },
                "summary": {
                    "total_income": str(income_total),
                    "total_expenses": str(expense_total),
                    "net_income": str(net_income),
                    "transaction_count": transactions.count(),
                },
                "income_by_category": list(income_by_category),
                "expense_by_category": list(expense_by_category),
            }
        )


class AccountingPeriodFilter(django_filters.FilterSet):
    property = django_filters.NumberFilter(field_name='property_obj', lookup_expr='exact')

    class Meta:
        model = AccountingPeriod
        fields = ['property', 'is_closed', 'period_type']


class AccountingPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing accounting periods.

    GET /api/accounting/periods/ - List accounting periods
    POST /api/accounting/periods/ - Create accounting period
    GET /api/accounting/periods/{id}/ - Get period details
    PUT /api/accounting/periods/{id}/ - Update period
    POST /api/accounting/periods/{id}/close/ - Close accounting period
    """

    serializer_class = AccountingPeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AccountingPeriodFilter
    ordering_fields = ["period_start", "period_end"]
    ordering = ["-period_start"]

    def get_queryset(self):
        """Filter accounting periods by user permissions"""
        user = self.request.user

        if user.user_type == "admin":
            return AccountingPeriod.objects.all()
        elif user.user_type in ["owner", "manager"]:
            return AccountingPeriod.objects.filter(property_obj__owner=user)
        else:
            return AccountingPeriod.objects.none()

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close an accounting period"""
        period = self.get_object()

        # Check permissions
        if period.property_obj.owner != request.user and request.user.user_type != "admin":
            return Response(
                {"error": "You do not have permission to close this period"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if period.is_closed:
            return Response(
                {"error": "Period is already closed"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate final totals
        period.calculate_totals()
        period.is_closed = True
        period.closed_at = timezone.now()
        period.closed_by = request.user
        period.save()

        serializer = self.get_serializer(period)
        return Response(serializer.data)
