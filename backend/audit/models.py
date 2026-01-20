from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

User = get_user_model()


class AuditLog(models.Model):
    """Audit log for tracking all changes in the system"""

    ACTION_CHOICES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Data Export'),
        ('report', 'Report Generated'),
        ('payment', 'Payment Processed'),
    )

    # Who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(max_length=150, help_text='Username at time of action')

    # What was affected
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_description = models.TextField(blank=True)

    # Data changes (for updates)
    old_values = models.JSONField(null=True, blank=True, help_text='Previous values')
    new_values = models.JSONField(null=True, blank=True, help_text='New values')

    # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)

    # Metadata
    timestamp = models.DateTimeField(default=timezone.now)
    app_label = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.username} {self.get_action_display()} {self.content_type.model} at {self.timestamp}"

    @property
    def changed_fields(self):
        """Get list of fields that were changed"""
        if not self.old_values or not self.new_values:
            return []

        return [
            field for field in self.new_values.keys()
            if self.old_values.get(field) != self.new_values.get(field)
        ]

    @property
    def is_sensitive_action(self):
        """Check if this action involves sensitive data"""
        sensitive_actions = ['delete', 'payment']
        sensitive_models = ['user', 'payment', 'billing']

        return (
            self.action in sensitive_actions or
            self.model_name.lower() in sensitive_models
        )


class AuditLogArchive(models.Model):
    """Archived audit logs for long-term storage"""

    original_id = models.PositiveIntegerField(unique=True)
    data = models.JSONField(help_text='Complete audit log data')
    archived_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-archived_at']
        indexes = [
            models.Index(fields=['original_id']),
            models.Index(fields=['archived_at']),
        ]

    def __str__(self):
        return f"Archived log {self.original_id}"