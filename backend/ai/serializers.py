"""
AI Serializers for TenantBase
API serializers for AI processing results and analysis data.
"""

from rest_framework import serializers
from .models import (
    AIProcessingResult,
    LeaseAnalysis,
    TenantApplicationAnalysis,
    MaintenanceAnalysis,
    PropertyInspection,
    WorkCompletionAnalysis,
    FinancialAnalysis,
    VoiceInteraction,
    VoiceReport
)


class AIProcessingResultSerializer(serializers.ModelSerializer):
    """Serializer for AI processing results."""

    # Related object names for better UX
    property_name = serializers.CharField(
        source='property_obj.name',
        read_only=True
    )
    tenant_name = serializers.CharField(
        source='tenant.full_name',
        read_only=True
    )
    lease_identifier = serializers.SerializerMethodField()
    maintenance_title = serializers.CharField(
        source='maintenance_request.title',
        read_only=True
    )

    class Meta:
        model = AIProcessingResult
        fields = [
            'id', 'processing_type', 'ai_model_used', 'confidence_score',
            'property_obj', 'property_name', 'tenant', 'tenant_name',
            'lease', 'lease_identifier', 'maintenance_request', 'maintenance_title',
            'structured_output', 'generated_content', 'status', 'error_message',
            'processing_time_ms', 'tokens_used', 'cost_estimate',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'processing_time_ms', 'tokens_used', 'cost_estimate'
        ]

    def get_lease_identifier(self, obj):
        """Get a readable identifier for the lease."""
        if obj.lease:
            return f"Lease {obj.lease.id} - {obj.lease.tenant.full_name}"
        return None


class LeaseAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for lease analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = LeaseAnalysis
        fields = [
            'id', 'ai_result', 'tenant_name', 'property_address',
            'monthly_rent', 'lease_start_date', 'lease_end_date',
            'security_deposit', 'pet_deposit', 'utilities_included',
            'special_terms', 'key_terms_summary', 'extraction_quality'
        ]
        read_only_fields = ['id']


class TenantApplicationAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for tenant application analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = TenantApplicationAnalysis
        fields = [
            'id', 'ai_result', 'applicant_name', 'current_address',
            'phone_number', 'email', 'employment_status', 'monthly_income',
            'credit_score', 'rental_history', 'risk_assessment',
            'recommendations', 'concerns', 'pets_info', 'move_in_timeline'
        ]
        read_only_fields = ['id']


class MaintenanceAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for maintenance analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)
    estimated_cost_range = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceAnalysis
        fields = [
            'id', 'ai_result', 'priority_assessment', 'estimated_cost_min',
            'estimated_cost_max', 'estimated_cost_range', 'required_skills',
            'parts_needed', 'safety_concerns', 'approach_recommendation',
            'timeline_estimate', 'vendor_needed', 'follow_up_required'
        ]
        read_only_fields = ['id']

    def get_estimated_cost_range(self, obj):
        """Format cost range for display."""
        if obj.estimated_cost_min and obj.estimated_cost_max:
            return f"${obj.estimated_cost_min:.2f} - ${obj.estimated_cost_max:.2f}"
        elif obj.estimated_cost_min:
            return f"From ${obj.estimated_cost_min:.2f}"
        elif obj.estimated_cost_max:
            return f"Up to ${obj.estimated_cost_max:.2f}"
        return None


class PropertyInspectionSerializer(serializers.ModelSerializer):
    """Serializer for property inspection analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = PropertyInspection
        fields = [
            'id', 'ai_result', 'inspection_type', 'room_area',
            'overall_condition', 'damage_description', 'maintenance_items',
            'safety_concerns', 'estimated_repair_cost', 'urgency_level',
            'recommendations', 'compliance_notes', 'photo_urls'
        ]
        read_only_fields = ['id']


class WorkCompletionAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for work completion analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = WorkCompletionAnalysis
        fields = [
            'id', 'ai_result', 'maintenance_request', 'completion_quality',
            'issues_resolved', 'remaining_issues', 'workmanship_quality',
            'compliance_check', 'follow_up_work', 'monitoring_needed',
            'before_photo_urls', 'after_photo_urls'
        ]
        read_only_fields = ['id']


# Input serializers for AI processing requests

class DocumentAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for document analysis requests."""

    document_content = serializers.CharField(
        required=True,
        help_text="Text content extracted from the document"
    )
    document_type = serializers.ChoiceField(
        choices=[
            ('lease', 'Lease Agreement'),
            ('application', 'Tenant Application'),
            ('contract', 'Other Contract'),
        ],
        required=True
    )
    property_id = serializers.IntegerField(
        required=False,
        help_text="Associated property ID (optional)"
    )
    tenant_id = serializers.IntegerField(
        required=False,
        help_text="Associated tenant ID (optional)"
    )


class MaintenanceAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for maintenance request analysis."""

    description = serializers.CharField(
        required=True,
        help_text="Description of the maintenance issue"
    )
    urgency = serializers.ChoiceField(
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        required=True
    )
    property_type = serializers.CharField(
        required=False,
        default='apartment',
        help_text="Type of property (apartment, house, etc.)"
    )
    maintenance_request_id = serializers.IntegerField(
        required=False,
        help_text="Associated maintenance request ID (optional)"
    )


class CommunicationRequestSerializer(serializers.Serializer):
    """Serializer for communication generation requests."""

    communication_type = serializers.ChoiceField(
        choices=[
            ('welcome_email', 'Tenant Welcome Email'),
            ('maintenance_response', 'Maintenance Response'),
            ('lease_reminder', 'Lease Renewal Reminder'),
            ('payment_reminder', 'Payment Reminder'),
        ],
        required=True
    )

    # Context data for different communication types
    tenant_name = serializers.CharField(required=False)
    property_address = serializers.CharField(required=False)
    move_in_date = serializers.DateField(required=False)
    issue_description = serializers.CharField(required=False)
    priority = serializers.CharField(required=False)
    estimated_time = serializers.CharField(required=False)
    lease_end_date = serializers.DateField(required=False)
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    due_date = serializers.DateField(required=False)


class PropertyImageAnalysisSerializer(serializers.Serializer):
    """Serializer for property image analysis requests."""

    image_description = serializers.CharField(
        required=True,
        help_text="Detailed description of what's visible in the property image"
    )
    inspection_type = serializers.ChoiceField(
        choices=[
            ('initial', 'Initial Inspection'),
            ('move_in', 'Move-in Inspection'),
            ('move_out', 'Move-out Inspection'),
            ('maintenance', 'Maintenance Inspection'),
            ('annual', 'Annual Inspection'),
            ('damage_assessment', 'Damage Assessment'),
        ],
        default='general',
        required=False
    )
    room_area = serializers.CharField(
        required=False,
        help_text="Specific room or area being inspected"
    )
    inspection_context = serializers.CharField(
        required=False,
        help_text="Additional context about the inspection"
    )
    property_id = serializers.IntegerField(
        required=False,
        help_text="Associated property ID"
    )
    photo_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        help_text="URLs of the inspection photos"
    )


class FinancialAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for financial analysis results."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = FinancialAnalysis
        fields = [
            'id', 'ai_result', 'analysis_period', 'report_type',
            'profitability_rating', 'financial_ratios', 'trend_analysis',
            'forecasts', 'risk_assessment', 'recommendations',
            'benchmarking_insights', 'investment_rating', 'expected_returns',
            'market_analysis', 'generated_report'
        ]
        read_only_fields = ['id']


class WorkCompletionAnalysisSerializer(serializers.Serializer):
    """Serializer for work completion analysis requests."""

    before_image_description = serializers.CharField(
        required=True,
        help_text="Description of the before-work image"
    )
    after_image_description = serializers.CharField(
        required=True,
        help_text="Description of the after-work image"
    )
    work_description = serializers.CharField(
        required=False,
        help_text="Description of the work that was performed"
    )
    maintenance_request_id = serializers.IntegerField(
        required=False,
        help_text="Associated maintenance request ID"
    )
    before_photo_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        help_text="URLs of before-work photos"
    )
    after_photo_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        help_text="URLs of after-work photos"
    )


class FinancialAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for financial analysis requests."""

    property_id = serializers.IntegerField(
        required=True,
        help_text="ID of the property to analyze"
    )
    analysis_period = serializers.ChoiceField(
        choices=[
            ('3_months', '3 Months'),
            ('6_months', '6 Months'),
            ('12_months', '12 Months'),
            ('24_months', '24 Months'),
        ],
        default='12_months',
        required=False,
        help_text="Period for financial analysis"
    )
    report_type = serializers.ChoiceField(
        choices=[
            ('monthly', 'Monthly Report'),
            ('quarterly', 'Quarterly Report'),
            ('annual', 'Annual Report'),
            ('forecast', 'Financial Forecast'),
        ],
        default='monthly',
        required=False,
        help_text="Type of financial report to generate"
    )
    include_market_data = serializers.BooleanField(
        default=False,
        help_text="Include market analysis and benchmarking"
    )


class InvestmentAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for investment analysis requests."""

    property_id = serializers.IntegerField(
        required=True,
        help_text="ID of the property to analyze for investment"
    )
    market_location = serializers.CharField(
        required=False,
        help_text="Location for market analysis (city, zip code, etc.)"
    )
    target_irr = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        help_text="Target Internal Rate of Return percentage"
    )
    hold_period_years = serializers.IntegerField(
        min_value=1,
        max_value=20,
        default=7,
        required=False,
        help_text="Expected holding period in years"
    )
    acquisition_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        help_text="Proposed acquisition price"
    )


class VoiceCommandSerializer(serializers.Serializer):
    """Serializer for voice command processing."""

    audio_transcript = serializers.CharField(
        required=True,
        help_text="Transcribed text from voice input"
    )
    audio_duration = serializers.FloatField(
        required=False,
        help_text="Duration of audio input in seconds"
    )
    user_context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="User context (properties, recent activities, etc.)"
    )


class VoiceReportRequestSerializer(serializers.Serializer):
    """Serializer for voice report generation."""

    report_type = serializers.ChoiceField(
        choices=[
            ('property_status', 'Property Status Report'),
            ('financial_summary', 'Financial Summary'),
            ('maintenance_overview', 'Maintenance Overview'),
            ('occupancy_update', 'Occupancy Update'),
            ('urgent_alerts', 'Urgent Alerts'),
        ],
        required=True,
        help_text="Type of voice report to generate"
    )
    property_id = serializers.IntegerField(
        required=False,
        help_text="Property ID for property-specific reports"
    )


class VoiceInteractionSerializer(serializers.ModelSerializer):
    """Serializer for voice interactions."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = VoiceInteraction
        fields = [
            'id', 'ai_result', 'interaction_type', 'audio_transcript',
            'audio_duration_seconds', 'audio_file_url', 'detected_intent',
            'intent_confidence', 'extracted_parameters', 'response_text',
            'response_audio_url', 'action_taken', 'action_result',
            'needs_clarification', 'clarification_question', 'suggested_follow_ups'
        ]
        read_only_fields = ['id']


class VoiceReportSerializer(serializers.ModelSerializer):
    """Serializer for voice reports."""

    ai_result = AIProcessingResultSerializer(read_only=True)

    class Meta:
        model = VoiceReport
        fields = [
            'id', 'ai_result', 'report_type', 'property_obj', 'report_text',
            'report_audio_url', 'audio_duration_seconds', 'key_highlights',
            'urgent_items', 'recommended_actions'
        ]
        read_only_fields = ['id']