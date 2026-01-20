from django.core.validators import MinValueValidator
from django.db import models


class FinancialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    CATEGORY_CHOICES = (
        # Income categories
        ("rent", "Rent Income"),
        ("late_fees", "Late Fees"),
        ("pet_deposit", "Pet Deposit"),
        ("security_deposit", "Security Deposit"),
        ("other_income", "Other Income"),
        # Expense categories
        ("maintenance", "Maintenance & Repairs"),
        ("utilities", "Utilities"),
        ("insurance", "Insurance"),
        ("property_tax", "Property Tax"),
        ("management_fees", "Property Management Fees"),
        ("marketing", "Marketing & Advertising"),
        ("legal_fees", "Legal Fees"),
        ("accounting_fees", "Accounting Fees"),
        ("supplies", "Office Supplies"),
        ("other_expenses", "Other Expenses"),
    )

    property_obj = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="financial_transactions"
    )

    # Transaction details
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    # Description and date
    description = models.TextField(blank=True)
    transaction_date = models.DateField()

    # Related entities (optional)
    lease = models.ForeignKey(
        "leases.Lease",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financial_transactions",
    )
    maintenance_request = models.ForeignKey(
        "maintenance.MaintenanceRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financial_transactions",
    )

    # Vendor/tenant information
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_invoice_number = models.CharField(max_length=100, blank=True)

    # Audit fields
    recorded_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="recorded_transactions"
    )

    # Recurring transaction support
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["property_obj"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["transaction_date"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.category} - ${self.amount}"

    def get_transaction_type_display(self):
        return dict(self.TRANSACTION_TYPE_CHOICES).get(self.transaction_type, self.transaction_type)

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class AccountingPeriod(models.Model):
    """Model to track accounting periods (months/quarters)"""

    property_obj = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="accounting_periods")

    # Period details
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(
        max_length=20,
        choices=[
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        default="monthly",
    )

    # Financial summaries
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Status
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_periods",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start"]
        unique_together = ("property_obj", "period_start", "period_end")

    def __str__(self):
        return f"{self.property_obj.property_name} - {self.period_start} to {self.period_end}"

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.total_income == 0:
            return 0
        return round((self.net_income / self.total_income) * 100, 2)

    def calculate_totals(self):
        """Calculate total income and expenses for this period"""
        from django.db.models import Sum

        income_total = (
            FinancialTransaction.objects.filter(
                property_obj=self.property_obj,
                transaction_type="income",
                transaction_date__gte=self.period_start,
                transaction_date__lte=self.period_end,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        expense_total = (
            FinancialTransaction.objects.filter(
                property_obj=self.property_obj,
                transaction_type="expense",
                transaction_date__gte=self.period_start,
                transaction_date__lte=self.period_end,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        self.total_income = income_total
        self.total_expenses = expense_total
        self.net_income = income_total - expense_total
        self.save()
