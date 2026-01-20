from rest_framework import serializers

from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    active_lease_count = serializers.SerializerMethodField()
    monthly_rent_total = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "address",
            "city",
            "state",
            "zip_code",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "employer_name",
            "employer_phone",
            "annual_income",
            "previous_landlord_name",
            "previous_landlord_phone",
            "is_active",
            "credit_score",
            "active_lease_count",
            "monthly_rent_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "active_lease_count",
            "monthly_rent_total",
        ]

    def get_full_name(self, obj):
        return obj.full_name

    def get_active_lease_count(self, obj):
        return obj.get_active_leases().count()

    def get_monthly_rent_total(self, obj):
        return str(obj.get_monthly_rent_total())
