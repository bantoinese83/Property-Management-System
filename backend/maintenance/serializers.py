from rest_framework import serializers

from .models import MaintenanceRequest


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.property_name", read_only=True)
    tenant_name = serializers.CharField(source="tenant.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_since_request = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRequest
        fields = [
            "id",
            "property",
            "property_name",
            "tenant",
            "tenant_name",
            "title",
            "description",
            "priority",
            "category",
            "status",
            "assigned_to",
            "assigned_to_name",
            "vendor_name",
            "vendor_phone",
            "vendor_email",
            "estimated_cost",
            "actual_cost",
            "requested_date",
            "scheduled_date",
            "completed_date",
            "images",
            "notes",
            "is_overdue",
            "days_since_request",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_overdue", "days_since_request"]

    def get_is_overdue(self, obj):
        return obj.is_overdue

    def get_days_since_request(self, obj):
        return obj.days_since_request
