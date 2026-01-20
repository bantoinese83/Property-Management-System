from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Lease(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("pending", "Pending Signature"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("terminated", "Terminated"),
    )

    property_obj = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="leases")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.SET_NULL, null=True, related_name="leases")

    # Dates
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    signed_date = models.DateField(null=True, blank=True)

    # Financial
    monthly_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    pet_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Documents
    lease_document_url = models.CharField(max_length=500, blank=True)

    # Status & Notes
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    auto_renew = models.BooleanField(default=True)
    renewal_notice_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(365)]
    )

    notes = models.TextField(blank=True)

    # Optimistic locking
    version = models.PositiveIntegerField(default=1, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("property_obj", "tenant", "lease_start_date")
        ordering = ["-lease_start_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["property_obj"]),
            models.Index(fields=["lease_end_date"]),
        ]

    def __str__(self):
        tenant_name = self.tenant.get_full_name() if self.tenant else "No Tenant"
        return f"Lease: {tenant_name} - {self.property_obj.property_name}"

    @property
    def days_remaining(self):
        """Calculate days remaining in lease with edge case handling"""
        try:
            if not self.lease_end_date:
                return 0
            today = timezone.now().date()
            days = (self.lease_end_date - today).days
            return max(0, days)  # Don't return negative days
        except (AttributeError, TypeError):
            return 0

    @property
    def is_ending_soon(self):
        """Check if lease is ending soon with edge case handling"""
        try:
            days_remaining = self.days_remaining
            return 0 <= days_remaining <= self.renewal_notice_days
        except (AttributeError, TypeError, ValueError):
            return False

    @property
    def is_expired(self):
        return timezone.now().date() > self.lease_end_date

    def save(self, *args, **kwargs):
        """Auto-update status based on dates with comprehensive edge case handling"""
        today = timezone.now().date()

        # Ensure dates are date objects, not strings
        if isinstance(self.lease_start_date, str):
            from datetime import datetime
            try:
                self.lease_start_date = datetime.strptime(self.lease_start_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                # Invalid date format, set to today as fallback
                self.lease_start_date = today

        if isinstance(self.lease_end_date, str):
            from datetime import datetime
            try:
                self.lease_end_date = datetime.strptime(self.lease_end_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                # Invalid date format, set to one year from start as fallback
                start_date = self.lease_start_date if hasattr(self, 'lease_start_date') and self.lease_start_date else today
                self.lease_end_date = start_date.replace(year=start_date.year + 1)

        # Validate date logic
        if hasattr(self, 'lease_start_date') and hasattr(self, 'lease_end_date'):
            if self.lease_end_date and self.lease_start_date and self.lease_end_date < self.lease_start_date:
                # Invalid date range, swap them or set end date to one year after start
                self.lease_end_date = self.lease_start_date.replace(year=self.lease_start_date.year + 1)

        # Auto-update status based on dates (only for non-terminated leases)
        if self.status != "terminated":
            try:
                if today > self.lease_end_date:
                    self.status = "expired"
                elif today >= self.lease_start_date:
                    self.status = "active"
                # If dates are in future, keep as draft/pending
            except (AttributeError, TypeError):
                # If date comparison fails, don't change status
                pass

        # Handle optimistic locking
        if self.pk:  # Only increment version for updates, not creates
            self.version += 1

        super().save(*args, **kwargs)
