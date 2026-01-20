from rest_framework import serializers

from .models import Lease


class LeaseSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    is_ending_soon = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)
    property_name = serializers.CharField(source="property_obj.property_name", read_only=True)

    class Meta:
        model = Lease
        fields = [
            "id",
            "property_obj",
            "property_name",
            "tenant",
            "tenant_name",
            "lease_start_date",
            "lease_end_date",
            "signed_date",
            "monthly_rent",
            "deposit_amount",
            "pet_deposit",
            "late_fee",
            "lease_document_url",
            "status",
            "auto_renew",
            "renewal_notice_days",
            "notes",
            "days_remaining",
            "is_ending_soon",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "days_remaining",
            "is_ending_soon",
            "is_expired",
        ]

    def get_days_remaining(self, obj):
        return obj.days_remaining

    def get_is_ending_soon(self, obj):
        return obj.is_ending_soon

    def get_is_expired(self, obj):
        return obj.is_expired

    def validate(self, data):
        if data.get("lease_end_date") and data.get("lease_start_date"):
            if data["lease_end_date"] <= data["lease_start_date"]:
                raise serializers.ValidationError(
                    {"lease_end_date": "End date must be after start date"}
                )
        return data
