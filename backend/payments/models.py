from django.core.validators import MinValueValidator
from django.db import models


class RentPayment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("credit_card", "Credit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("check", "Check"),
        ("cash", "Cash"),
        ("online", "Online Payment"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    )

    lease_obj = models.ForeignKey("leases.Lease", on_delete=models.CASCADE, related_name="payments")

    # Payment details
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateField()
    due_date = models.DateField()

    # Payment method and status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Transaction details
    transaction_id = models.CharField(max_length=255, blank=True)
    payment_processor = models.CharField(max_length=50, blank=True)  # stripe, paypal, etc.

    # Additional information
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    # Audit fields
    processed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payments",
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-payment_date"]
        unique_together = ("lease_obj", "payment_date")  # One payment per lease per month
        indexes = [
            models.Index(fields=["lease_obj"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"Payment: {self.lease_obj} - {self.amount} ({self.get_status_display()})"

    @property
    def is_late(self):
        """Check if payment is late"""
        from django.utils import timezone

        return self.status == "overdue" or (
            self.status in ["pending", "failed"] and timezone.now().date() > self.due_date
        )

    @property
    def total_amount(self):
        """Total amount including late fees"""
        return self.amount + self.late_fee

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)
