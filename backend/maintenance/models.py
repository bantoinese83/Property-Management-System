from django.db import models
from django.core.validators import MinValueValidator

class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    )

    property_obj = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_requests'
    )

    # Request details
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True)

    # Status and assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )

    # Vendor information
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_phone = models.CharField(max_length=20, blank=True)
    vendor_email = models.EmailField(blank=True)

    # Cost and timing
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # Dates
    requested_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    # Images and notes
    images = models.JSONField(default=list, blank=True)  # Array of image URLs
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['property_obj']),
            models.Index(fields=['requested_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.property_obj.property_name}"

    @property
    def is_overdue(self):
        """Check if maintenance request is overdue"""
        from django.utils import timezone
        if self.scheduled_date and self.status not in ['completed', 'closed']:
            return timezone.now() > self.scheduled_date
        return False

    @property
    def days_since_request(self):
        """Calculate days since request was made"""
        from django.utils import timezone
        return (timezone.now() - self.requested_date).days

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)
