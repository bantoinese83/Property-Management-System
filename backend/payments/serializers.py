from rest_framework import serializers
from .models import RentPayment

class RentPaymentSerializer(serializers.ModelSerializer):
    lease_property_name = serializers.CharField(source='lease.property.property_name', read_only=True)
    lease_tenant_name = serializers.CharField(source='lease.tenant.full_name', read_only=True)
    is_late = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = RentPayment
        fields = [
            'id', 'lease', 'lease_property_name', 'lease_tenant_name',
            'amount', 'payment_date', 'due_date', 'payment_method', 'status',
            'transaction_id', 'payment_processor', 'late_fee', 'total_amount',
            'notes', 'processed_by', 'processed_by_name', 'processed_at',
            'is_late', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_late', 'total_amount'
        ]

    def get_is_late(self, obj):
        return obj.is_late

    def get_total_amount(self, obj):
        return str(obj.total_amount)