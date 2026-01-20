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

    def validate_monthly_rent(self, value):
        if value < 0:
            raise serializers.ValidationError("Monthly rent cannot be negative")
        if value > 100000:  # Reasonable upper limit
            raise serializers.ValidationError("Monthly rent cannot exceed $100,000")
        return value

    def validate_deposit_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Deposit amount cannot be negative")
        return value

    def validate_pet_deposit(self, value):
        if value < 0:
            raise serializers.ValidationError("Pet deposit cannot be negative")
        return value

    def validate_late_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Late fee cannot be negative")
        if value > 10000:  # Reasonable upper limit
            raise serializers.ValidationError("Late fee cannot exceed $10,000")
        return value

    def validate_renewal_notice_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Renewal notice days cannot be negative")
        if value > 365:
            raise serializers.ValidationError("Renewal notice days cannot exceed 365")
        return value

    def validate_lease_start_date(self, value):
        from datetime import date
        today = date.today()
        if value < today.replace(year=today.year - 10):  # Not too far in the past
            raise serializers.ValidationError("Lease start date cannot be more than 10 years in the past")
        if value > today.replace(year=today.year + 2):  # Not too far in the future
            raise serializers.ValidationError("Lease start date cannot be more than 2 years in the future")
        return value

    def validate_lease_end_date(self, value):
        from datetime import date
        today = date.today()
        if value < today:  # Allow past dates for historical leases
            pass  # We'll handle expired leases in the model
        if value > today.replace(year=today.year + 20):  # Not too far in the future
            raise serializers.ValidationError("Lease end date cannot be more than 20 years in the future")
        return value

    def validate_signed_date(self, value):
        if value is not None:
            from datetime import date
            today = date.today()
            if value > today:
                raise serializers.ValidationError("Signed date cannot be in the future")
            if value < today.replace(year=today.year - 10):
                raise serializers.ValidationError("Signed date cannot be more than 10 years in the past")
        return value

    def validate(self, data):
        # Enhanced date validation
        start_date = data.get("lease_start_date")
        end_date = data.get("lease_end_date")
        signed_date = data.get("signed_date")

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({"lease_end_date": "End date must be after start date"})

            # Check for reasonable lease duration (not too short or too long)
            duration_days = (end_date - start_date).days
            if duration_days < 30:  # Minimum 1 month
                raise serializers.ValidationError("Lease duration must be at least 30 days")
            if duration_days > 3650:  # Maximum 10 years
                raise serializers.ValidationError("Lease duration cannot exceed 10 years")

        if signed_date and start_date:
            if signed_date > start_date:
                raise serializers.ValidationError({"signed_date": "Signed date cannot be after lease start date"})

        # Validate financial relationships
        monthly_rent = data.get("monthly_rent")
        deposit_amount = data.get("deposit_amount")

        if monthly_rent and deposit_amount is not None:
            if deposit_amount > monthly_rent * 6:  # Deposit shouldn't be more than 6 months rent
                raise serializers.ValidationError({"deposit_amount": "Deposit amount seems unreasonably high"})

        return data
