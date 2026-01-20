from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class SubscriptionPlan(models.Model):
    """Subscription plans for the property management system"""

    PLAN_TYPES = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    )

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    interval = models.CharField(max_length=20, choices=[
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ], default='month')

    # Feature limits (use -1 for unlimited)
    max_properties = models.IntegerField(default=1, help_text="Use -1 for unlimited")
    max_tenants = models.IntegerField(default=10, help_text="Use -1 for unlimited")
    max_users = models.IntegerField(default=1, help_text="Use -1 for unlimited")
    storage_limit_mb = models.PositiveIntegerField(default=100)

    # Features
    features = models.JSONField(default=dict, help_text="Plan features as JSON")

    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} (${self.price}/{self.interval})"


class Subscription(models.Model):
    """User subscriptions"""

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)

    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_active(self):
        return self.status == 'active' and not self.cancel_at_period_end


class PaymentMethod(models.Model):
    """User payment methods"""

    METHOD_TYPES = (
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)

    # For cards
    last4 = models.CharField(max_length=4, blank=True)
    brand = models.CharField(max_length=50, blank=True)  # visa, mastercard, etc.
    exp_month = models.PositiveIntegerField(null=True, blank=True)
    exp_year = models.PositiveIntegerField(null=True, blank=True)

    # For bank accounts
    bank_name = models.CharField(max_length=100, blank=True)
    account_last4 = models.CharField(max_length=4, blank=True)

    # Stripe integration
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        if self.method_type == 'card':
            return f"{self.brand.title()} ****{self.last4}"
        else:
            return f"{self.bank_name} ****{self.account_last4}"


class Invoice(models.Model):
    """Invoices for billing"""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Dates
    invoice_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Stripe integration
    stripe_invoice_id = models.CharField(max_length=100, blank=True, unique=True)
    stripe_invoice_url = models.URLField(blank=True)

    # Invoice details
    description = models.TextField(blank=True)
    line_items = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.id} - {self.user.username} - ${self.amount}"