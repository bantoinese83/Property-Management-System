"""
AI Serializers for TenantBase
API serializers for AI processing results and analysis data.
"""

from rest_framework import serializers
from .models import (
    AIProcessingResult,
    LeaseAnalysis,
    TenantApplicationAnalysis,
    MaintenanceAnalysis
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