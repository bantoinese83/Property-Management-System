from rest_framework import serializers
from .models import Property, PropertyImage

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_primary', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class PropertySerializer(serializers.ModelSerializer):
    occupancy_rate = serializers.SerializerMethodField()
    monthly_income = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    full_address = serializers.CharField(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'owner_name', 'property_name', 'description',
            'address', 'city', 'state', 'zip_code', 'country',
            'latitude', 'longitude', 'full_address',
            'property_type', 'total_units', 'year_built',
            'square_footage', 'bedrooms', 'bathrooms',
            'purchase_price', 'purchase_date',
            'annual_property_tax', 'insurance_cost',
            'is_active', 'is_listed_for_rent',
            'occupancy_rate', 'monthly_income',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'occupancy_rate', 'monthly_income'
        ]

    def get_occupancy_rate(self, obj):
        return obj.get_occupancy_rate()

    def get_monthly_income(self, obj):
        return str(obj.get_monthly_income())

    def validate_total_units(self, value):
        if value < 1:
            raise serializers.ValidationError("Total units must be at least 1")
        return value

class PropertyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    occupancy_rate = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'property_name', 'address', 'city', 'state',
            'property_type', 'total_units', 'is_active',
            'occupancy_rate', 'owner_name', 'created_at'
        ]

    def get_occupancy_rate(self, obj):
        return obj.get_occupancy_rate()