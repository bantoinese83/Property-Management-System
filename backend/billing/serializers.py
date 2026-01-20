from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, PaymentMethod, Invoice


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price', max_digits=10, decimal_places=2, read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_name', 'plan_price', 'status', 'current_period_start',
            'current_period_end', 'cancel_at_period_end', 'is_active', 'days_until_expiry'
        ]
        read_only_fields = ['id', 'is_active']

    def get_days_until_expiry(self, obj):
        if obj.current_period_end:
            from django.utils import timezone
            delta = obj.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0


class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'last4', 'brand', 'exp_month', 'exp_year',
            'bank_name', 'account_last4', 'is_default', 'display_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_display_name(self, obj):
        if obj.method_type == 'card':
            return f"{obj.brand.title()} ****{obj.last4}"
        else:
            return f"{obj.bank_name} ****{obj.account_last4}"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'stripe_invoice_id', 'stripe_invoice_url', 'created_at', 'updated_at']