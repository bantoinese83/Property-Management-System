"""
AI Models for TenantBase
Stores AI processing results, analysis data, and metadata.
"""

from django.db import models
from django.conf import settings


class AIProcessingResult(models.Model):
    """Base model for AI processing results."""

    PROCESSING_TYPES = [
        ('lease_analysis', 'Lease Document Analysis'),
        ('tenant_application', 'Tenant Application Analysis'),
        ('maintenance_request', 'Maintenance Request Analysis'),
        ('property_inspection', 'Property Inspection Analysis'),
        ('communication', 'Generated Communication'),
        ('financial_analysis', 'Financial Report Analysis'),
    ]

    # Associated entities (nullable foreign keys)
    property_obj = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_processing_results'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_processing_results'
    )
    lease = models.ForeignKey(
        'leases.Lease',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_processing_results'
    )
    maintenance_request = models.ForeignKey(
        'maintenance.MaintenanceRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_processing_results'
    )

    # AI Processing Details
    processing_type = models.CharField(
        max_length=50,
        choices=PROCESSING_TYPES,
        help_text="Type of AI processing performed"
    )
    ai_model_used = models.CharField(
        max_length=100,
        help_text="AI model used for processing (e.g., gemini-2.5-pro)"
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score of AI analysis (0.0 to 1.0)"
    )

    # Input/Output Data
    input_text = models.TextField(
        help_text="Original text input to AI processing"
    )
    structured_output = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured JSON output from AI processing"
    )
    generated_content = models.TextField(
        null=True,
        blank=True,
        help_text="Generated content (emails, summaries, etc.)"
    )

    # Metadata
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken for AI processing in milliseconds"
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of tokens used in AI processing"
    )
    cost_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Estimated cost of AI processing in USD"
    )

    # Status and Error Handling
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if processing failed"
    )

    # Audit Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_processing_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['processing_type', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['property_obj', 'processing_type']),
            models.Index(fields=['tenant', 'processing_type']),
        ]

    def __str__(self):
        return f"{self.processing_type} - {self.status} ({self.created_at.date()})"


class LeaseAnalysis(models.Model):
    """Specific model for lease document analysis results."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='lease_analysis'
    )

    # Extracted lease data
    tenant_name = models.CharField(max_length=200, null=True, blank=True)
    property_address = models.TextField(null=True, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lease_start_date = models.DateField(null=True, blank=True)
    lease_end_date = models.DateField(null=True, blank=True)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pet_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Additional extracted data
    utilities_included = models.JSONField(null=True, blank=True)  # List of utilities
    special_terms = models.TextField(null=True, blank=True)
    key_terms_summary = models.TextField(null=True, blank=True)

    # Analysis metadata
    extraction_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        null=True,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['lease_start_date', 'lease_end_date']),
        ]


class TenantApplicationAnalysis(models.Model):
    """Specific model for tenant application analysis results."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='tenant_application_analysis'
    )

    # Extracted applicant data
    applicant_name = models.CharField(max_length=200, null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_score = models.IntegerField(null=True, blank=True)

    # Analysis results
    rental_history = models.TextField(null=True, blank=True)
    risk_assessment = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
        ],
        null=True,
        blank=True
    )
    recommendations = models.TextField(null=True, blank=True)
    concerns = models.JSONField(null=True, blank=True)  # List of concerns

    # Pets and other details
    pets_info = models.TextField(null=True, blank=True)
    move_in_timeline = models.CharField(max_length=100, null=True, blank=True)


class MaintenanceAnalysis(models.Model):
    """Specific model for maintenance request analysis results."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='maintenance_analysis'
    )

    # Analysis results
    priority_assessment = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        null=True,
        blank=True
    )
    estimated_cost_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_cost_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Technical details
    required_skills = models.JSONField(null=True, blank=True)  # List of skills
    parts_needed = models.JSONField(null=True, blank=True)  # List of parts
    safety_concerns = models.TextField(null=True, blank=True)

    # Recommendations
    approach_recommendation = models.TextField(null=True, blank=True)
    timeline_estimate = models.CharField(max_length=100, null=True, blank=True)
    vendor_needed = models.BooleanField(default=False)
    follow_up_required = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['priority_assessment']),
        ]