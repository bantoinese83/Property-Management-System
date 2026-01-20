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

    property_obj = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="leases"
    )
    tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.SET_NULL, null=True, related_name="leases"
    )

    # Dates
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    signed_date = models.DateField(null=True, blank=True)

    # Financial
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pet_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Documents
    lease_document_url = models.CharField(max_length=500, blank=True)

    # Status & Notes
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    auto_renew = models.BooleanField(default=True)
    renewal_notice_days = models.IntegerField(default=30)

    notes = models.TextField(blank=True)

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
        return (self.lease_end_date - timezone.now().date()).days

    @property
    def is_ending_soon(self):
        return 0 <= self.days_remaining <= self.renewal_notice_days

    @property
    def is_expired(self):
        return timezone.now().date() > self.lease_end_date

    def save(self, *args, **kwargs):
        """Auto-update status based on dates"""
        today = timezone.now().date()

        if self.status != "terminated":
            if today > self.lease_end_date:
                self.status = "expired"
            elif today >= self.lease_start_date:
                self.status = "active"

        super().save(*args, **kwargs)
