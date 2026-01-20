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


class PropertyInspection(models.Model):
    """Specific model for property inspection analysis results."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='property_inspection'
    )

    # Inspection details
    inspection_type = models.CharField(
        max_length=50,
        choices=[
            ('initial', 'Initial Inspection'),
            ('move_in', 'Move-in Inspection'),
            ('move_out', 'Move-out Inspection'),
            ('maintenance', 'Maintenance Inspection'),
            ('annual', 'Annual Inspection'),
            ('damage_assessment', 'Damage Assessment'),
        ],
        help_text="Type of property inspection performed"
    )
    room_area = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific room or area inspected"
    )

    # AI assessment results
    overall_condition = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        null=True,
        blank=True
    )
    damage_description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of any damage or issues found"
    )
    maintenance_items = models.JSONField(
        null=True,
        blank=True,
        help_text="List of maintenance items identified"
    )
    safety_concerns = models.TextField(
        null=True,
        blank=True,
        help_text="Any safety issues or hazards detected"
    )

    # Cost and priority assessment
    estimated_repair_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost for repairs needed"
    )
    urgency_level = models.CharField(
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

    # Recommendations and notes
    recommendations = models.TextField(
        null=True,
        blank=True,
        help_text="Specific recommendations for property manager"
    )
    compliance_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Code compliance or regulatory concerns"
    )

    # Photo references (if stored)
    photo_urls = models.JSONField(
        null=True,
        blank=True,
        help_text="URLs or references to inspection photos"
    )

    class Meta:
        indexes = [
            models.Index(fields=['inspection_type', 'overall_condition']),
            models.Index(fields=['urgency_level']),
        ]


class WorkCompletionAnalysis(models.Model):
    """Model for before/after work completion analysis."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='work_completion_analysis'
    )

    # Associated maintenance request
    maintenance_request = models.ForeignKey(
        'maintenance.MaintenanceRequest',
        on_delete=models.CASCADE,
        related_name='work_completion_analyses',
        null=True,
        blank=True
    )

    # Work assessment
    completion_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('satisfactory', 'Satisfactory'),
            ('poor', 'Poor'),
            ('incomplete', 'Incomplete'),
        ],
        null=True,
        blank=True
    )
    issues_resolved = models.JSONField(
        null=True,
        blank=True,
        help_text="List of issues that appear resolved"
    )
    remaining_issues = models.JSONField(
        null=True,
        blank=True,
        help_text="Any remaining problems identified"
    )

    # Quality assessment
    workmanship_quality = models.TextField(
        null=True,
        blank=True,
        help_text="Assessment of work quality"
    )
    compliance_check = models.CharField(
        max_length=20,
        choices=[
            ('compliant', 'Compliant'),
            ('non_compliant', 'Non-compliant'),
            ('unknown', 'Unknown'),
        ],
        null=True,
        blank=True
    )

    # Recommendations
    follow_up_work = models.TextField(
        null=True,
        blank=True,
        help_text="Any follow-up work recommended"
    )
    monitoring_needed = models.BooleanField(
        default=False,
        help_text="Whether ongoing monitoring is needed"
    )

    # Photo references
    before_photo_urls = models.JSONField(
        null=True,
        blank=True,
        help_text="URLs to before-work photos"
    )
    after_photo_urls = models.JSONField(
        null=True,
        blank=True,
        help_text="URLs to after-work photos"
    )


class FinancialAnalysis(models.Model):
    """Model for property financial analysis results."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='financial_analysis'
    )

    # Analysis metadata
    analysis_period = models.CharField(
        max_length=20,
        choices=[
            ('3_months', '3 Months'),
            ('6_months', '6 Months'),
            ('12_months', '12 Months'),
            ('24_months', '24 Months'),
            ('custom', 'Custom Period'),
        ],
        default='12_months',
        help_text="Period covered by this financial analysis"
    )
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly Report'),
            ('quarterly', 'Quarterly Report'),
            ('annual', 'Annual Report'),
            ('investment', 'Investment Analysis'),
            ('forecast', 'Financial Forecast'),
        ],
        default='monthly',
        help_text="Type of financial report or analysis"
    )

    # Financial health assessment
    profitability_rating = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        null=True,
        blank=True
    )

    # Key financial metrics (stored as JSON for flexibility)
    financial_ratios = models.JSONField(
        null=True,
        blank=True,
        help_text="Key financial ratios and metrics"
    )
    trend_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Revenue, expense, and profit trends"
    )
    forecasts = models.JSONField(
        null=True,
        blank=True,
        help_text="Financial projections and forecasts"
    )

    # Risk assessment
    risk_assessment = models.JSONField(
        null=True,
        blank=True,
        help_text="Financial risks and mitigation strategies"
    )

    # Recommendations and insights
    recommendations = models.JSONField(
        null=True,
        blank=True,
        help_text="Specific recommendations for improvement"
    )
    benchmarking_insights = models.TextField(
        null=True,
        blank=True,
        help_text="How property compares to market benchmarks"
    )

    # Investment analysis (for investment reports)
    investment_rating = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent Investment'),
            ('good', 'Good Investment'),
            ('fair', 'Fair Investment'),
            ('poor', 'Poor Investment'),
            ('high_risk', 'High Risk - Avoid'),
        ],
        null=True,
        blank=True
    )
    expected_returns = models.JSONField(
        null=True,
        blank=True,
        help_text="Projected returns and IRR calculations"
    )
    market_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text="Market conditions and competitive positioning"
    )

    # Generated reports
    generated_report = models.TextField(
        null=True,
        blank=True,
        help_text="Full generated financial report content"
    )

    class Meta:
        indexes = [
            models.Index(fields=['analysis_period', 'report_type']),
            models.Index(fields=['profitability_rating']),
            models.Index(fields=['investment_rating']),
        ]


class VoiceInteraction(models.Model):
    """Model for voice assistant interactions."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='voice_interaction'
    )

    # Voice interaction details
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ('command', 'Voice Command'),
            ('report', 'Voice Report'),
            ('status_check', 'Status Check'),
            ('reminder', 'Voice Reminder'),
            ('help', 'Help Request'),
        ],
        help_text="Type of voice interaction"
    )

    # Audio data
    audio_transcript = models.TextField(
        help_text="Transcribed text from voice input"
    )
    audio_duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration of the audio input in seconds"
    )
    audio_file_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to stored audio file"
    )

    # AI processing results
    detected_intent = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="AI-detected intent from voice command"
    )
    intent_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score for intent detection"
    )
    extracted_parameters = models.JSONField(
        null=True,
        blank=True,
        help_text="Parameters extracted from voice command"
    )

    # Response data
    response_text = models.TextField(
        null=True,
        blank=True,
        help_text="Text response generated by AI"
    )
    response_audio_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to generated audio response"
    )

    # Action tracking
    action_taken = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Action that was taken based on voice command"
    )
    action_result = models.JSONField(
        null=True,
        blank=True,
        help_text="Result of the action taken"
    )

    # Follow-up
    needs_clarification = models.BooleanField(
        default=False,
        help_text="Whether the command needs clarification"
    )
    clarification_question = models.TextField(
        null=True,
        blank=True,
        help_text="Question to ask for clarification"
    )
    suggested_follow_ups = models.JSONField(
        null=True,
        blank=True,
        help_text="Suggested follow-up actions or questions"
    )

    class Meta:
        indexes = [
            models.Index(fields=['interaction_type', 'detected_intent']),
            models.Index(fields=['needs_clarification']),
        ]


class VoiceReport(models.Model):
    """Model for generated voice reports."""

    ai_result = models.OneToOneField(
        AIProcessingResult,
        on_delete=models.CASCADE,
        related_name='voice_report'
    )

    # Report details
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('property_status', 'Property Status Report'),
            ('financial_summary', 'Financial Summary'),
            ('maintenance_overview', 'Maintenance Overview'),
            ('occupancy_update', 'Occupancy Update'),
            ('urgent_alerts', 'Urgent Alerts'),
        ],
        help_text="Type of voice report generated"
    )

    # Associated entity
    property_obj = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='voice_reports'
    )

    # Report content
    report_text = models.TextField(
        help_text="Full text content of the voice report"
    )
    report_audio_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to the generated audio report"
    )
    audio_duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration of the audio report"
    )

    # Report metadata
    key_highlights = models.JSONField(
        null=True,
        blank=True,
        help_text="Key highlights or summary points"
    )
    urgent_items = models.JSONField(
        null=True,
        blank=True,
        help_text="Urgent items mentioned in the report"
    )
    recommended_actions = models.JSONField(
        null=True,
        blank=True,
        help_text="Recommended actions from the report"
    )

    class Meta:
        indexes = [
            models.Index(fields=['report_type', 'property_obj']),
        ]