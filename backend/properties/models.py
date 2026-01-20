"""
Property models for the Property Management System.

This module contains all models related to property management,
including properties, property images, and related functionality.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Property(models.Model):
    """
    Represents a rental property in the system.

    This model stores all information about a property that can be rented out,
    including physical details, financial information, and management data.

    Attributes:
        owner (ForeignKey): The user who owns this property
        property_name (str): Human-readable name for the property
        description (str): Optional detailed description
        address (str): Street address
        city (str): City name
        state (str): State/province code
        zip_code (str): Postal code
        country (str): Country (defaults to USA)
        latitude/longitude (Decimal): Geographic coordinates for mapping
        property_type (str): Type of property (apartment, house, etc.)
        total_units (int): Number of rentable units
        year_built (int): Year the property was constructed
        square_footage (int): Total square footage
        bedrooms/bathrooms (int/Decimal): Unit specifications
        purchase_price (Decimal): Original purchase cost
        purchase_date (Date): When the property was acquired
        annual_property_tax (Decimal): Annual tax amount
        insurance_cost (Decimal): Annual insurance cost
        is_active (bool): Whether property is currently managed
        is_listed_for_rent (bool): Whether property is available for rent
        created_at/updated_at (DateTime): Audit timestamps
    """
    PROPERTY_TYPE_CHOICES = (
        ("single_family", "Single Family Home"),
        ("apartment", "Apartment"),
        ("condo", "Condo"),
        ("townhouse", "Townhouse"),
        ("duplex", "Duplex"),
        ("commercial", "Commercial"),
        ("industrial", "Industrial"),
        ("other", "Other"),
    )

    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="properties")
    property_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Address
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="USA")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Property Details
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    total_units = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    year_built = models.IntegerField(null=True, blank=True)
    square_footage = models.IntegerField(null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    # Financial
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    annual_property_tax = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_listed_for_rent = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("owner", "address", "city")
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["property_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.property_name} - {self.address}"

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"

    def get_occupancy_rate(self):
        """Calculate occupancy percentage"""
        from leases.models import Lease

        today = timezone.now().date()
        active_leases = Lease.objects.filter(
            property_obj=self, status="active", lease_start_date__lte=today, lease_end_date__gte=today
        ).count()

        if self.total_units == 0:
            return 0
        return round((active_leases / self.total_units) * 100, 2)

    def get_monthly_income(self):
        """Calculate expected monthly income from all active leases"""
        from leases.models import Lease

        today = timezone.now().date()
        total_rent = Lease.objects.filter(
            property_obj=self, status="active", lease_start_date__lte=today, lease_end_date__gte=today
        ).aggregate(total=models.Sum("monthly_rent"))["total"]

        return total_rent or 0


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/")
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Image for {self.property.property_name}"
