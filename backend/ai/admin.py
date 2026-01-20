"""
AI Admin for TenantBase
Django admin configuration for AI models.
"""

from django.contrib import admin
from .models import (
    AIProcessingResult,
    LeaseAnalysis,
    TenantApplicationAnalysis,
    MaintenanceAnalysis
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