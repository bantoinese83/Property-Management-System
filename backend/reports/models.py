from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Report(models.Model):
    """Generated reports storage"""

    REPORT_TYPES = (
        ("financial_summary", "Financial Summary"),
        ("property_performance", "Property Performance"),
        ("tenant_report", "Tenant Report"),
        ("maintenance_report", "Maintenance Report"),
        ("occupancy_report", "Occupancy Report"),
        ("revenue_analysis", "Revenue Analysis"),
        ("expense_analysis", "Expense Analysis"),
        ("custom", "Custom Report"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)

    # Report parameters
    parameters = models.JSONField(default=dict, help_text="Report generation parameters")

    # Generation details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_reports")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Report output
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)

    # Date range
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

    @property
    def is_ready(self):
        return self.status == "completed" and self.file_path

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=["download_count"])


class ReportTemplate(models.Model):
    """Pre-configured report templates"""

    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=Report.REPORT_TYPES)

    # Default parameters
    default_parameters = models.JSONField(default=dict)

    # Template metadata
    category = models.CharField(max_length=100, default="general")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.display_name
