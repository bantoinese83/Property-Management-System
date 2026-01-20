from datetime import date
from rest_framework import serializers

from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "caption", "is_primary", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class PropertySerializer(serializers.ModelSerializer):
    occupancy_rate = serializers.SerializerMethodField()
    monthly_income = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    full_address = serializers.CharField(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "owner",
            "owner_name",
            "property_name",
            "description",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "latitude",
            "longitude",
            "full_address",
            "property_type",
            "total_units",
            "year_built",
            "square_footage",
            "bedrooms",
            "bathrooms",
            "purchase_price",
            "purchase_date",
            "annual_property_tax",
            "insurance_cost",
            "is_active",
            "is_listed_for_rent",
            "occupancy_rate",
            "monthly_income",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_name", "created_at", "updated_at", "occupancy_rate", "monthly_income"]

    def get_occupancy_rate(self, obj):
        return obj.get_occupancy_rate()

    def get_monthly_income(self, obj):
        return str(obj.get_monthly_income())

    def validate_total_units(self, value):
        if value < 1:
            raise serializers.ValidationError("Total units must be at least 1")
        if value > 10000:  # Reasonable upper limit
            raise serializers.ValidationError("Total units cannot exceed 10,000")
        return value

    def validate_year_built(self, value):
        if value is not None:
            current_year = date.today().year
            if value < 1800:
                raise serializers.ValidationError("Year built cannot be before 1800")
            if value > current_year + 1:
                raise serializers.ValidationError("Year built cannot be in the future")
        return value

    def validate_square_footage(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Square footage must be positive")
        return value

    def validate_bedrooms(self, value):
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Bedrooms cannot be negative")
            if value > 50:
                raise serializers.ValidationError("Bedrooms cannot exceed 50")
        return value

    def validate_bathrooms(self, value):
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Bathrooms cannot be negative")
            if value > 20:
                raise serializers.ValidationError("Bathrooms cannot exceed 20")
        return value

    def validate_purchase_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Purchase price cannot be negative")
        return value

    def validate_annual_property_tax(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Annual property tax cannot be negative")
        return value

    def validate_insurance_cost(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Insurance cost cannot be negative")
        return value

    def validate_latitude(self, value):
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        return value

    def validate_longitude(self, value):
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        return value

    def validate_zip_code(self, value):
        """Validate ZIP code format"""
        import re
        if value and not re.match(r'^\d{5}(-\d{4})?$', value):
            raise serializers.ValidationError("Enter a valid ZIP code (e.g., 12345 or 12345-6789).")
        return value


class PropertyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""

    occupancy_rate = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "property_name",
            "address",
            "city",
            "state",
            "property_type",
            "total_units",
            "is_active",
            "occupancy_rate",
            "owner_name",
            "created_at",
        ]

    def get_occupancy_rate(self, obj):
        return obj.get_occupancy_rate()
