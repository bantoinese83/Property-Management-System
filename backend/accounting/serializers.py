from rest_framework import serializers

from .models import AccountingPeriod, FinancialTransaction


class FinancialTransactionSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.property_name", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = FinancialTransaction
        fields = [
            "id",
            "property",
            "property_name",
            "transaction_type",
            "category",
            "amount",
            "description",
            "transaction_date",
            "lease",
            "maintenance_request",
            "vendor_name",
            "vendor_invoice_number",
            "recorded_by",
            "recorded_by_name",
            "is_recurring",
            "recurring_frequency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AccountingPeriodSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.property_name", read_only=True)
    closed_by_name = serializers.CharField(source="closed_by.get_full_name", read_only=True)
    profit_margin = serializers.SerializerMethodField()

    class Meta:
        model = AccountingPeriod
        fields = [
            "id",
            "property",
            "property_name",
            "period_start",
            "period_end",
            "period_type",
            "total_income",
            "total_expenses",
            "net_income",
            "profit_margin",
            "is_closed",
            "closed_at",
            "closed_by",
            "closed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "profit_margin"]

    def get_profit_margin(self, obj):
        return obj.profit_margin
