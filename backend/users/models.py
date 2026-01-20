from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date


class User(AbstractUser):
    """Custom user model with extended fields"""

    USER_TYPE_CHOICES = (
        ("admin", "Administrator"),
        ("manager", "Property Manager"),
        ("owner", "Property Owner"),
        ("tenant", "Tenant"),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="owner")
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
            message='Enter a valid phone number.',
            code='invalid_phone_number'
        )]
    )
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\d{5}(-\d{4})?$',
            message='Enter a valid ZIP code.',
            code='invalid_zip_code'
        )]
    )
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["user_type"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type)

    def clean(self):
        """Validate user data"""
        from django.core.exceptions import ValidationError

        # Validate date of birth is not in the future and not too old
        if self.date_of_birth:
            today = date.today()
            if self.date_of_birth > today:
                raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future.'})
            # Check if user is not unreasonably old (over 150 years)
            if (today - self.date_of_birth).days > (150 * 365):
                raise ValidationError({'date_of_birth': 'Invalid date of birth.'})

        super().clean()


class UserProfile(models.Model):
    """Extended user profile for additional data"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    notification_preferences = models.JSONField(default=dict, help_text="User's notification preferences")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Notification(models.Model):
    """User notifications"""

    NOTIFICATION_TYPES = (
        ("system", "System Notification"),
        ("payment", "Payment Notification"),
        ("maintenance", "Maintenance Notification"),
        ("lease", "Lease Notification"),
        ("property", "Property Notification"),
        ("tenant", "Tenant Notification"),
    )

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    # Related objects (optional)
    related_model = models.CharField(max_length=100, blank=True)  # e.g., 'property', 'lease', 'maintenance'
    related_id = models.PositiveIntegerField(null=True, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    # Metadata
    action_url = models.URLField(blank=True)  # URL to redirect user to
    metadata = models.JSONField(default=dict)  # Additional data

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "notification_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=["is_read", "updated_at"])

    def archive(self):
        """Archive notification"""
        self.is_archived = True
        self.save(update_fields=["is_archived", "updated_at"])


class NotificationPreference(models.Model):
    """User notification preferences"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_preferences")

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_payment_reminders = models.BooleanField(default=True)
    email_maintenance_updates = models.BooleanField(default=True)
    email_lease_updates = models.BooleanField(default=True)
    email_system_updates = models.BooleanField(default=True)

    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_payment_reminders = models.BooleanField(default=True)
    in_app_maintenance_updates = models.BooleanField(default=True)
    in_app_lease_updates = models.BooleanField(default=True)
    in_app_system_updates = models.BooleanField(default=True)

    # Push notification preferences (for future mobile app)
    push_enabled = models.BooleanField(default=False)
    push_payment_reminders = models.BooleanField(default=False)
    push_maintenance_updates = models.BooleanField(default=False)
    push_lease_updates = models.BooleanField(default=False)
    push_system_updates = models.BooleanField(default=False)

    # Frequency settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ("immediate", "Immediate"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("never", "Never"),
        ],
        default="immediate",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"


# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile automatically when User is created"""
    if created:
        UserProfile.objects.create(user=instance)
