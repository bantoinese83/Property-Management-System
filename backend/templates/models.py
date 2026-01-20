from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DocumentTemplate(models.Model):
    """Templates for generating documents"""

    TEMPLATE_TYPES = (
        ("lease", "Lease Agreement"),
        ("notice", "Notice/Letter"),
        ("report", "Report"),
        ("contract", "Contract"),
        ("form", "Form"),
    )

    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=100, default="general")

    # Template content
    content = models.TextField(help_text="Template content with {{variable}} placeholders")

    # Metadata
    variables = models.JSONField(default=list, help_text="List of variables used in template")
    is_active = models.BooleanField(default=True)
    is_system_template = models.BooleanField(default=False)

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_templates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.display_name} ({self.get_template_type_display()})"

    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        from django.utils import timezone

        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=["usage_count", "last_used"])


class GeneratedDocument(models.Model):
    """Documents generated from templates"""

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("sent", "Sent"),
        ("signed", "Signed"),
    )

    title = models.CharField(max_length=255)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, related_name="generated_documents")

    # Content and data
    content = models.TextField()
    variables_data = models.JSONField(help_text="Variable values used for generation")
    generated_content = models.TextField(blank=True)

    # File storage
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Recipients (for sent documents)
    recipient_emails = models.JSONField(default=list, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Related entities
    related_model = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'property', 'lease', 'tenant'
    related_id = models.PositiveIntegerField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="generated_documents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def is_ready(self):
        return self.status in ["generated", "sent", "signed"] and self.generated_content
