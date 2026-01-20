"""
Property models for the Property Management System.

This module contains all models related to property management,
including properties, property images, and related functionality.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from datetime import date


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
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    # Property Details
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    total_units = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    year_built = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(date.today().year + 1)]
    )
    square_footage = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    bedrooms = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )

    # Financial
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    purchase_date = models.DateField(null=True, blank=True)
    annual_property_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    insurance_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_listed_for_rent = models.BooleanField(default=True)

    # Optimistic locking
    version = models.PositiveIntegerField(default=1, editable=False)

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
        """Calculate occupancy percentage with edge case handling"""
        from leases.models import Lease

        # Handle edge case where total_units is invalid
        if not self.total_units or self.total_units <= 0:
            return 0.0

        today = timezone.now().date()
        try:
            active_leases = Lease.objects.filter(
                property_obj=self, status="active",
                lease_start_date__lte=today,
                lease_end_date__gte=today
            ).count()
        except Exception:
            # Handle database query errors gracefully
            return 0.0

        # Prevent division by zero (redundant but defensive)
        if self.total_units == 0:
            return 0.0

        occupancy_rate = (active_leases / self.total_units) * 100
        return round(max(0.0, min(100.0, occupancy_rate)), 2)

    def save(self, *args, **kwargs):
        """Handle optimistic locking"""
        if self.pk:  # Only increment version for updates, not creates
            self.version += 1
        super().save(*args, **kwargs)

    def get_monthly_income(self):
        """Calculate expected monthly income from all active leases with edge case handling"""
        from leases.models import Lease

        today = timezone.now().date()
        try:
            result = Lease.objects.filter(
                property_obj=self, status="active",
                lease_start_date__lte=today,
                lease_end_date__gte=today
            ).aggregate(total=models.Sum("monthly_rent"))
            total_rent = result.get("total")
        except Exception:
            # Handle database query errors gracefully
            return 0

        # Ensure we return a valid decimal or 0
        if total_rent is None:
            return 0
        return max(0, total_rent)


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
