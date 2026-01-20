from django.db import models


class Tenant(models.Model):
    """Tenant model for lease holders"""

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Address information (current residence)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    # Employment information
    employer_name = models.CharField(max_length=255, blank=True)
    employer_phone = models.CharField(max_length=20, blank=True)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # References
    previous_landlord_name = models.CharField(max_length=150, blank=True)
    previous_landlord_phone = models.CharField(max_length=20, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    credit_score = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_active_leases(self):
        """Get all active leases for this tenant"""
        from django.utils import timezone
        from leases.models import Lease

        today = timezone.now().date()
        return Lease.objects.filter(
            tenant=self, status="active", lease_start_date__lte=today, lease_end_date__gte=today
        )

    def get_monthly_rent_total(self):
        """Get total monthly rent across all active leases"""
        active_leases = self.get_active_leases()
        return sum(lease.monthly_rent for lease in active_leases)
