"""
AI Admin for TenantBase
Django admin configuration for AI models.
"""

from django.contrib import admin
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


@admin.register(AIProcessingResult)
class AIProcessingResultAdmin(admin.ModelAdmin):
    """Admin for AI processing results."""

    list_display = [
        'id', 'processing_type', 'status', 'ai_model_used',
        'confidence_score', 'created_at', 'created_by'
    ]
    list_filter = ['processing_type', 'status', 'ai_model_used', 'created_at']
    search_fields = ['input_text', 'generated_content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Processing Info', {
            'fields': ('processing_type', 'ai_model_used', 'status', 'confidence_score')
        }),
        ('Related Entities', {
            'fields': ('property_obj', 'tenant', 'lease', 'maintenance_request'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('input_text', 'structured_output', 'generated_content'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('processing_time_ms', 'tokens_used', 'cost_estimate', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LeaseAnalysis)
class LeaseAnalysisAdmin(admin.ModelAdmin):
    """Admin for lease analysis results."""

    list_display = [
        'id', 'tenant_name', 'monthly_rent', 'lease_start_date',
        'extraction_quality', 'ai_result'
    ]
    list_filter = ['extraction_quality', 'lease_start_date', 'lease_end_date']
    search_fields = ['tenant_name', 'property_address', 'special_terms']
    readonly_fields = ['id']

    fieldsets = (
        ('Lease Data', {
            'fields': ('tenant_name', 'property_address', 'monthly_rent',
                      'lease_start_date', 'lease_end_date', 'security_deposit', 'pet_deposit')
        }),
        ('Additional Details', {
            'fields': ('utilities_included', 'special_terms', 'key_terms_summary'),
            'classes': ('collapse',)
        }),
        ('Analysis Quality', {
            'fields': ('extraction_quality', 'ai_result'),
        }),
    )


@admin.register(TenantApplicationAnalysis)
class TenantApplicationAnalysisAdmin(admin.ModelAdmin):
    """Admin for tenant application analysis results."""

    list_display = [
        'id', 'applicant_name', 'monthly_income', 'risk_assessment',
        'ai_result'
    ]
    list_filter = ['risk_assessment', 'employment_status']
    search_fields = ['applicant_name', 'email', 'current_address']
    readonly_fields = ['id']

    fieldsets = (
        ('Applicant Info', {
            'fields': ('applicant_name', 'current_address', 'phone_number', 'email')
        }),
        ('Financial & Employment', {
            'fields': ('employment_status', 'monthly_income', 'credit_score'),
            'classes': ('collapse',)
        }),
        ('Analysis Results', {
            'fields': ('rental_history', 'risk_assessment', 'recommendations', 'concerns'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('pets_info', 'move_in_timeline', 'ai_result'),
        }),
    )


@admin.register(MaintenanceAnalysis)
class MaintenanceAnalysisAdmin(admin.ModelAdmin):
    """Admin for maintenance analysis results."""

    list_display = [
        'id', 'priority_assessment', 'estimated_cost_min',
        'vendor_needed', 'ai_result'
    ]
    list_filter = ['priority_assessment', 'vendor_needed', 'follow_up_required']
    search_fields = ['approach_recommendation', 'safety_concerns']
    readonly_fields = ['id']

    fieldsets = (
        ('Assessment', {
            'fields': ('priority_assessment', 'estimated_cost_min', 'estimated_cost_max')
        }),
        ('Technical Details', {
            'fields': ('required_skills', 'parts_needed', 'safety_concerns'),
            'classes': ('collapse',)
        }),
        ('Recommendations', {
            'fields': ('approach_recommendation', 'timeline_estimate',
                      'vendor_needed', 'follow_up_required'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('ai_result',),
        }),
    )


@admin.register(PropertyInspection)
class PropertyInspectionAdmin(admin.ModelAdmin):
    """Admin for property inspection analysis results."""

    list_display = [
        'id', 'inspection_type', 'room_area', 'overall_condition',
        'urgency_level', 'estimated_repair_cost', 'ai_result'
    ]
    list_filter = ['inspection_type', 'overall_condition', 'urgency_level']
    search_fields = ['room_area', 'damage_description', 'safety_concerns']
    readonly_fields = ['id']

    fieldsets = (
        ('Inspection Details', {
            'fields': ('inspection_type', 'room_area')
        }),
        ('Assessment Results', {
            'fields': ('overall_condition', 'damage_description', 'maintenance_items',
                      'safety_concerns', 'estimated_repair_cost', 'urgency_level'),
            'classes': ('collapse',)
        }),
        ('Recommendations', {
            'fields': ('recommendations', 'compliance_notes'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('photo_urls', 'ai_result'),
        }),
    )


@admin.register(WorkCompletionAnalysis)
class WorkCompletionAnalysisAdmin(admin.ModelAdmin):
    """Admin for work completion analysis results."""

    list_display = [
        'id', 'completion_quality', 'compliance_check',
        'monitoring_needed', 'ai_result'
    ]
    list_filter = ['completion_quality', 'compliance_check', 'monitoring_needed']
    search_fields = ['workmanship_quality', 'follow_up_work']
    readonly_fields = ['id']

    fieldsets = (
        ('Work Assessment', {
            'fields': ('completion_quality', 'issues_resolved', 'remaining_issues'),
            'classes': ('collapse',)
        }),
        ('Quality & Compliance', {
            'fields': ('workmanship_quality', 'compliance_check'),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': ('follow_up_work', 'monitoring_needed'),
            'classes': ('collapse',)
        }),
        ('Media & Links', {
            'fields': ('before_photo_urls', 'after_photo_urls', 'maintenance_request', 'ai_result'),
        }),
    )


@admin.register(FinancialAnalysis)
class FinancialAnalysisAdmin(admin.ModelAdmin):
    """Admin for financial analysis results."""

    list_display = [
        'id', 'analysis_period', 'report_type', 'profitability_rating',
        'investment_rating', 'ai_result'
    ]
    list_filter = ['analysis_period', 'report_type', 'profitability_rating', 'investment_rating']
    search_fields = ['benchmarking_insights', 'recommendations']
    readonly_fields = ['id']

    fieldsets = (
        ('Analysis Details', {
            'fields': ('analysis_period', 'report_type', 'profitability_rating')
        }),
        ('Financial Metrics', {
            'fields': ('financial_ratios', 'trend_analysis', 'forecasts'),
            'classes': ('collapse',)
        }),
        ('Risk & Investment', {
            'fields': ('risk_assessment', 'investment_rating', 'expected_returns'),
            'classes': ('collapse',)
        }),
        ('Market Analysis', {
            'fields': ('market_analysis', 'benchmarking_insights'),
            'classes': ('collapse',)
        }),
        ('Recommendations', {
            'fields': ('recommendations', 'generated_report'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('ai_result',),
        }),
    )


@admin.register(VoiceInteraction)
class VoiceInteractionAdmin(admin.ModelAdmin):
    """Admin for voice interactions."""

    list_display = [
        'id', 'interaction_type', 'detected_intent', 'intent_confidence',
        'needs_clarification', 'action_taken', 'ai_result'
    ]
    list_filter = ['interaction_type', 'detected_intent', 'needs_clarification']
    search_fields = ['audio_transcript', 'response_text', 'detected_intent']
    readonly_fields = ['id']

    fieldsets = (
        ('Interaction Details', {
            'fields': ('interaction_type', 'audio_transcript', 'audio_duration_seconds')
        }),
        ('AI Processing', {
            'fields': ('detected_intent', 'intent_confidence', 'extracted_parameters'),
            'classes': ('collapse',)
        }),
        ('Response', {
            'fields': ('response_text', 'response_audio_url'),
            'classes': ('collapse',)
        }),
        ('Actions', {
            'fields': ('action_taken', 'action_result', 'needs_clarification', 'clarification_question'),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': ('suggested_follow_ups', 'ai_result'),
        }),
    )


@admin.register(VoiceReport)
class VoiceReportAdmin(admin.ModelAdmin):
    """Admin for voice reports."""

    list_display = [
        'id', 'report_type', 'property_obj', 'audio_duration_seconds',
        'ai_result'
    ]
    list_filter = ['report_type']
    search_fields = ['report_text']
    readonly_fields = ['id']

    fieldsets = (
        ('Report Details', {
            'fields': ('report_type', 'property_obj', 'report_text')
        }),
        ('Audio', {
            'fields': ('report_audio_url', 'audio_duration_seconds'),
            'classes': ('collapse',)
        }),
        ('Content Analysis', {
            'fields': ('key_highlights', 'urgent_items', 'recommended_actions'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('ai_result',),
        }),
    )