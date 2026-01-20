from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, URLValidator

class User(AbstractUser):
    """Custom user model with extended fields"""

    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('manager', 'Property Manager'),
        ('owner', 'Property Owner'),
        ('tenant', 'Tenant'),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='owner'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type)


class UserProfile(models.Model):
    """Extended user profile for additional data"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    notification_preferences = models.JSONField(
        default=dict,
        help_text="User's notification preferences"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
