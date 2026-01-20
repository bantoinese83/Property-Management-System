"""
AI Views for TenantBase
API endpoints for AI-powered document processing, analysis, and communication generation.
"""

import logging
from typing import Optional, Dict, Any

from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
from .serializers import (
    AIProcessingResultSerializer,
    LeaseAnalysisSerializer,
    TenantApplicationAnalysisSerializer,
    MaintenanceAnalysisSerializer,
    PropertyInspectionSerializer,
    WorkCompletionAnalysisSerializer,
    FinancialAnalysisSerializer,
    VoiceInteractionSerializer,
    VoiceReportSerializer,
    DocumentAnalysisRequestSerializer,
    MaintenanceAnalysisRequestSerializer,
    CommunicationRequestSerializer,
    PropertyImageAnalysisSerializer,
    FinancialAnalysisRequestSerializer,
    InvestmentAnalysisRequestSerializer,
    VoiceCommandSerializer,
    VoiceReportRequestSerializer
)
from .services import (
    document_service,
    communication_service,
    maintenance_service,
    inspection_service,
    financial_service,
    voice_service
)

logger = logging.getLogger(__name__)


class AIProcessingResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI processing results."""

    serializer_class = AIProcessingResultSerializer
    permission_classes = [IsAuthenticated]
    queryset = AIProcessingResult.objects.all()

    def get_queryset(self):
        """Filter results based on user's permissions."""
        user = self.request.user
        queryset = AIProcessingResult.objects.all()

        # Filter based on user role and associated entities
        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                # Tenants can only see results related to themselves
                queryset = queryset.filter(tenant__user=user)
            elif user.user_type == 'property_manager':
                # Property managers can see results for their properties
                queryset = queryset.filter(
                    property_obj__owner=user
                ) | queryset.filter(
                    property_obj__managers=user
                )

        return queryset.order_by('-created_at')


class LeaseAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for lease analysis results."""

    serializer_class = LeaseAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = LeaseAnalysis.objects.all()

    def get_queryset(self):
        """Filter lease analyses based on user permissions."""
        user = self.request.user
        queryset = LeaseAnalysis.objects.select_related('ai_result')

        if hasattr(user, 'user_type'):
            if user.user_type == 'tenant':
                queryset = queryset.filter(ai_result__tenant__user=user)
            elif user.user_type == 'property_manager':
                queryset = queryset.filter(
                    ai_result__property_obj__owner=user
                ) | queryset.filter(
                    ai_result__property_obj__managers=user
                )

        return queryset


class TenantApplicationAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tenant application analysis results."""

    serializer_class = TenantApplicationAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = TenantApplicationAnalysis.objects.all()

    def get_queryset(self):
        """Filter application analyses based on user permissions."""
        user = self.request.user
        queryset = TenantApplicationAnalysis.objects.select_related('ai_result')

        if hasattr(user, 'user_type') and user.user_type == 'property_manager':
            queryset = queryset.filter(
                ai_result__property_obj__owner=user
            ) | queryset.filter(
                ai_result__property_obj__managers=user
            )

        return queryset


class MaintenanceAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for maintenance analysis results."""

    serializer_class = MaintenanceAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = MaintenanceAnalysis.objects.all()


class PropertyInspectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for property inspection analysis results."""

    serializer_class = PropertyInspectionSerializer
    permission_classes = [IsAuthenticated]
    queryset = PropertyInspection.objects.all()


class WorkCompletionAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for work completion analysis results."""

    serializer_class = WorkCompletionAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = WorkCompletionAnalysis.objects.all()


class FinancialAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for financial analysis results."""

    serializer_class = FinancialAnalysisSerializer
    permission_classes = [IsAuthenticated]
    queryset = FinancialAnalysis.objects.all()


class VoiceInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for voice interactions."""

    serializer_class = VoiceInteractionSerializer
    permission_classes = [IsAuthenticated]
    queryset = VoiceInteraction.objects.all()


class VoiceReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for voice reports."""

    serializer_class = VoiceReportSerializer
    permission_classes = [IsAuthenticated]
    queryset = VoiceReport.objects.all()

    def get_queryset(self):
        """Filter maintenance analyses based on user permissions."""
        user = self.request.user
        queryset = MaintenanceAnalysis.objects.select_related('ai_result')

        if hasattr(user, 'user_type') and user.user_type == 'property_manager':
            queryset = queryset.filter(
                ai_result__maintenance_request__property__owner=user
            ) | queryset.filter(
                ai_result__maintenance_request__property__managers=user
            )

        return queryset


class AIServiceViewSet(viewsets.ViewSet):
    """ViewSet for AI processing services."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def analyze_document(self, request):
        """
        Analyze a document (lease or tenant application) using AI.
        """
        serializer = DocumentAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        document_content = data['document_content']
        document_type = data['document_type']

        # Check if AI service is available
        if not document_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type=f"{document_type}_analysis",
                ai_model_used="gemini-2.5-pro",
                input_text=document_content[:5000],  # Store truncated input
                status="processing",
                created_by=request.user,

                # Associate with related entities if provided
                property_obj_id=data.get('property_id'),
                tenant_id=data.get('tenant_id'),
            )

            result_data = None
            analysis_obj = None

            if document_type == 'lease':
                result_data = document_service.extract_lease_data(document_content)
                if result_data:
                    analysis_obj = LeaseAnalysis.objects.create(
                        ai_result=ai_result,
                        tenant_name=result_data.get('tenant_name'),
                        property_address=result_data.get('property_address'),
                        monthly_rent=result_data.get('monthly_rent'),
                        lease_start_date=result_data.get('lease_start_date'),
                        lease_end_date=result_data.get('lease_end_date'),
                        security_deposit=result_data.get('security_deposit'),
                        pet_deposit=result_data.get('pet_deposit'),
                        utilities_included=result_data.get('utilities_included'),
                        special_terms=result_data.get('special_terms'),
                    )

            elif document_type == 'application':
                result_data = document_service.analyze_tenant_application(document_content)
                if result_data:
                    analysis_obj = TenantApplicationAnalysis.objects.create(
                        ai_result=ai_result,
                        applicant_name=result_data.get('applicant_name'),
                        current_address=result_data.get('current_address'),
                        phone_number=result_data.get('phone_number'),
                        email=result_data.get('email'),
                        employment_status=result_data.get('employment_status'),
                        monthly_income=result_data.get('monthly_income'),
                        credit_score=result_data.get('credit_score_mentioned'),
                        rental_history=result_data.get('rental_history'),
                        risk_assessment=result_data.get('risk_assessment'),
                        recommendations=result_data.get('recommendations'),
                        pets_info=result_data.get('pets'),
                        move_in_timeline=result_data.get('move_in_timeline'),
                    )

            # Update the AI result with processed data
            ai_result.status = "completed"
            ai_result.structured_output = result_data
            ai_result.confidence_score = result_data.get('confidence_score') if result_data else None
            ai_result.save()

            # Return the appropriate serialized response
            if analysis_obj and document_type == 'lease':
                serializer = LeaseAnalysisSerializer(analysis_obj)
            elif analysis_obj and document_type == 'application':
                serializer = TenantApplicationAnalysisSerializer(analysis_obj)
            else:
                serializer = AIProcessingResultSerializer(ai_result)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to analyze document. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze_maintenance(self, request):
        """
        Analyze a maintenance request using AI.
        """
        serializer = MaintenanceAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not maintenance_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="maintenance_request",
                ai_model_used="gemini-2.5-pro",
                input_text=data['description'],
                status="processing",
                created_by=request.user,
                maintenance_request_id=data.get('maintenance_request_id'),
            )

            # Analyze maintenance request
            analysis_data = maintenance_service.analyze_maintenance_request(
                description=data['description'],
                urgency=data['urgency'],
                property_type=data.get('property_type', 'apartment')
            )

            if analysis_data:
                analysis_obj = MaintenanceAnalysis.objects.create(
                    ai_result=ai_result,
                    priority_assessment=analysis_data.get('priority_assessment'),
                    estimated_cost_min=self._parse_cost_range(analysis_data.get('estimated_cost', ''), 'min'),
                    estimated_cost_max=self._parse_cost_range(analysis_data.get('estimated_cost', ''), 'max'),
                    required_skills=analysis_data.get('required_skills'),
                    parts_needed=analysis_data.get('parts_needed'),
                    safety_concerns=analysis_data.get('safety_concerns'),
                    approach_recommendation=analysis_data.get('recommendations'),
                    timeline_estimate=analysis_data.get('timeline_estimate'),
                    vendor_needed=analysis_data.get('vendor_needed', False),
                    follow_up_required=analysis_data.get('follow_up_required', False),
                )

                ai_result.status = "completed"
                ai_result.structured_output = analysis_data
                ai_result.confidence_score = analysis_data.get('confidence_score')
                ai_result.save()

                serializer = MaintenanceAnalysisSerializer(analysis_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI analysis returned no results"
                ai_result.save()

                return Response(
                    {"error": "Could not analyze maintenance request. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error in maintenance analysis: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to analyze maintenance request. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_communication(self, request):
        """
        Generate automated communications using AI.
        """
        serializer = CommunicationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        communication_type = data['communication_type']

        if not communication_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            generated_content = None

            if communication_type == 'welcome_email':
                generated_content = communication_service.generate_tenant_welcome_email(
                    tenant_name=data.get('tenant_name', ''),
                    property_address=data.get('property_address', ''),
                    move_in_date=str(data.get('move_in_date', ''))
                )

            elif communication_type == 'maintenance_response':
                generated_content = communication_service.generate_maintenance_response(
                    issue_description=data.get('issue_description', ''),
                    priority=data.get('priority', 'medium'),
                    estimated_time=data.get('estimated_time', 'within 24 hours')
                )

            if generated_content:
                # Create AI processing result record
                ai_result = AIProcessingResult.objects.create(
                    processing_type="communication",
                    ai_model_used="gemini-2.5-flash",
                    input_text=f"Generated {communication_type} communication",
                    generated_content=generated_content,
                    status="completed",
                    created_by=request.user,
                )

                return Response({
                    "id": ai_result.id,
                    "communication_type": communication_type,
                    "generated_content": generated_content,
                    "created_at": ai_result.created_at,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Could not generate communication. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error generating communication: {e}")
            return Response(
                {"error": "Failed to generate communication. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze_property_image(self, request):
        """
        Analyze a property inspection image using AI.
        """
        serializer = PropertyImageAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not inspection_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="property_inspection",
                ai_model_used="gemini-2.5-pro",
                input_text=data['image_description'],
                status="processing",
                created_by=request.user,
                property_obj_id=data.get('property_id'),
            )

            # Analyze the property image
            analysis_data = inspection_service.analyze_property_image(
                image_description=data['image_description'],
                inspection_context=data.get('inspection_context', '')
            )

            if analysis_data:
                inspection_obj = PropertyInspection.objects.create(
                    ai_result=ai_result,
                    inspection_type=data.get('inspection_type', 'general'),
                    room_area=data.get('room_area', ''),
                    overall_condition=analysis_data.get('overall_condition'),
                    damage_description=analysis_data.get('damage_assessment'),
                    maintenance_items=analysis_data.get('maintenance_needed'),
                    safety_concerns=analysis_data.get('safety_concerns'),
                    estimated_repair_cost=self._parse_cost_estimate(analysis_data.get('estimated_costs')),
                    urgency_level=analysis_data.get('urgency_level'),
                    recommendations=analysis_data.get('recommendations'),
                    compliance_notes=analysis_data.get('compliance_notes'),
                    photo_urls=data.get('photo_urls'),
                )

                ai_result.status = "completed"
                ai_result.structured_output = analysis_data
                ai_result.confidence_score = analysis_data.get('confidence_score')
                ai_result.save()

                serializer = PropertyInspectionSerializer(inspection_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI analysis returned no results"
                ai_result.save()

                return Response(
                    {"error": "Could not analyze property image. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error in property image analysis: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to analyze property image. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze_work_completion(self, request):
        """
        Analyze before/after images of completed work.
        """
        serializer = WorkCompletionAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not inspection_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="work_completion",
                ai_model_used="gemini-2.5-pro",
                input_text=f"Work completion analysis: {data.get('work_description', '')}",
                status="processing",
                created_by=request.user,
                maintenance_request_id=data.get('maintenance_request_id'),
            )

            # Analyze work completion
            analysis_data = inspection_service.compare_before_after_images(
                before_description=data['before_image_description'],
                after_description=data['after_image_description'],
                work_description=data.get('work_description', '')
            )

            if analysis_data:
                completion_obj = WorkCompletionAnalysis.objects.create(
                    ai_result=ai_result,
                    maintenance_request_id=data.get('maintenance_request_id'),
                    completion_quality=analysis_data.get('work_completion_quality'),
                    issues_resolved=analysis_data.get('issues_resolved'),
                    remaining_issues=analysis_data.get('remaining_issues'),
                    workmanship_quality=analysis_data.get('quality_assessment'),
                    compliance_check=analysis_data.get('compliance_check'),
                    follow_up_work=analysis_data.get('recommendations'),
                    monitoring_needed=analysis_data.get('monitoring_needed', False),
                    before_photo_urls=data.get('before_photo_urls'),
                    after_photo_urls=data.get('after_photo_urls'),
                )

                ai_result.status = "completed"
                ai_result.structured_output = analysis_data
                ai_result.confidence_score = analysis_data.get('confidence_score')
                ai_result.save()

                serializer = WorkCompletionAnalysisSerializer(completion_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI analysis returned no results"
                ai_result.save()

                return Response(
                    {"error": "Could not analyze work completion. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error in work completion analysis: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to analyze work completion. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze_financials(self, request):
        """
        Analyze property financial performance using AI.
        """
        serializer = FinancialAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        property_id = data['property_id']

        if not financial_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Get property and gather financial data
            from properties.models import Property
            from leases.models import Lease
            from payments.models import RentPayment
            from accounting.models import FinancialTransaction

            try:
                property_obj = Property.objects.get(id=property_id)
            except Property.DoesNotExist:
                return Response(
                    {"error": "Property not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Gather financial data for the property
            financial_data = self._gather_property_financial_data(
                property_obj,
                data['analysis_period']
            )

            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="financial_analysis",
                ai_model_used="gemini-2.5-pro",
                input_text=f"Financial analysis for property {property_id}",
                status="processing",
                created_by=request.user,
                property_obj=property_obj,
            )

            # Analyze financial performance
            analysis_data = financial_service.analyze_property_financials(
                financial_data=financial_data,
                analysis_period=data['analysis_period']
            )

            if analysis_data:
                analysis_obj = FinancialAnalysis.objects.create(
                    ai_result=ai_result,
                    analysis_period=data['analysis_period'],
                    report_type=data['report_type'],
                    profitability_rating=analysis_data.get('profitability_assessment'),
                    financial_ratios=analysis_data.get('key_financial_ratios'),
                    trend_analysis=analysis_data.get('trend_analysis'),
                    forecasts=analysis_data.get('forecast_12_months'),
                    risk_assessment=analysis_data.get('risk_assessment'),
                    recommendations=analysis_data.get('recommendations'),
                    benchmarking_insights=analysis_data.get('benchmarking_insights'),
                )

                ai_result.status = "completed"
                ai_result.structured_output = analysis_data
                ai_result.confidence_score = analysis_data.get('confidence_score')
                ai_result.save()

                serializer = FinancialAnalysisSerializer(analysis_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI analysis returned no results"
                ai_result.save()

                return Response(
                    {"error": "Could not analyze financial data. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error in financial analysis: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to analyze financial data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_financial_report(self, request):
        """
        Generate a comprehensive financial report using AI.
        """
        serializer = FinancialAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        property_id = data['property_id']

        if not financial_service.is_available():
            return Response(
                {"error": "AI service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Get property and gather financial data
            from properties.models import Property

            try:
                property_obj = Property.objects.get(id=property_id)
            except Property.DoesNotExist:
                return Response(
                    {"error": "Property not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Gather comprehensive property data
            property_data = self._gather_comprehensive_property_data(property_obj)

            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="financial_report",
                ai_model_used="gemini-2.5-pro",
                input_text=f"Financial report generation for property {property_id}",
                status="processing",
                created_by=request.user,
                property_obj=property_obj,
            )

            # Generate financial report
            report_content = financial_service.generate_financial_report(
                property_data=property_data,
                report_type=data['report_type']
            )

            if report_content:
                analysis_obj = FinancialAnalysis.objects.create(
                    ai_result=ai_result,
                    analysis_period=data['analysis_period'],
                    report_type=data['report_type'],
                    generated_report=report_content,
                )

                ai_result.status = "completed"
                ai_result.generated_content = report_content
                ai_result.save()

                return Response({
                    "id": analysis_obj.id,
                    "report_type": data['report_type'],
                    "generated_report": report_content,
                    "created_at": ai_result.created_at,
                }, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI report generation failed"
                ai_result.save()

                return Response(
                    {"error": "Could not generate financial report. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error generating financial report: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to generate financial report. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def process_voice_command(self, request):
        """
        Process voice commands for property management.
        """
        serializer = VoiceCommandSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not voice_service.is_available():
            return Response(
                {"error": "Voice service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="voice_command",
                ai_model_used="gemini-2.5-pro",
                input_text=data['audio_transcript'],
                status="processing",
                created_by=request.user,
            )

            # Get user context for better voice responses
            user_context = self._get_user_context(request.user, data.get('user_context', {}))

            # Process voice command
            voice_result = voice_service.process_voice_command(
                audio_transcript=data['audio_transcript'],
                user_context=user_context
            )

            if voice_result:
                interaction_obj = VoiceInteraction.objects.create(
                    ai_result=ai_result,
                    interaction_type='command',
                    audio_transcript=data['audio_transcript'],
                    audio_duration_seconds=data.get('audio_duration'),
                    detected_intent=voice_result.get('intent'),
                    intent_confidence=voice_result.get('confidence'),
                    extracted_parameters=voice_result.get('parameters'),
                    response_text=voice_result.get('response_text'),
                    response_audio_url=voice_result.get('audio_response_url'),
                    needs_clarification=voice_result.get('needs_clarification', False),
                    clarification_question=voice_result.get('clarification_question'),
                    suggested_follow_ups=voice_result.get('suggested_actions'),
                )

                # Execute the detected intent if confidence is high enough
                if voice_result.get('confidence', 0) > 0.7:
                    action_result = self._execute_voice_intent(
                        voice_result.get('intent'),
                        voice_result.get('parameters', {}),
                        request.user
                    )
                    if action_result:
                        interaction_obj.action_taken = action_result.get('action')
                        interaction_obj.action_result = action_result.get('result')
                        interaction_obj.save()

                ai_result.status = "completed"
                ai_result.structured_output = voice_result
                ai_result.confidence_score = voice_result.get('confidence')
                ai_result.save()

                serializer = VoiceInteractionSerializer(interaction_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI voice processing failed"
                ai_result.save()

                return Response(
                    {"error": "Could not process voice command. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to process voice command. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_voice_report(self, request):
        """
        Generate voice reports for hands-free consumption.
        """
        serializer = VoiceReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not voice_service.is_available():
            return Response(
                {"error": "Voice service is not configured. Please check GEMINI_API_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Create AI processing result record
            ai_result = AIProcessingResult.objects.create(
                processing_type="voice_report",
                ai_model_used="gemini-2.5-flash",
                input_text=f"Generating {data['report_type']} voice report",
                status="processing",
                created_by=request.user,
            )

            # Get user context
            user_context = self._get_user_context(request.user, {})

            # Generate voice report
            if data['report_type'] == 'property_status' and data.get('property_id'):
                report_data = voice_service.generate_property_report_voice(
                    property_id=data['property_id'],
                    user_context=user_context
                )
            else:
                # Generic report generation - could be expanded
                report_data = {
                    'report_text': f"This is a {data['report_type']} voice report generated for {request.user.get_full_name() or request.user.username}.",
                    'audio_url': voice_service._generate_audio_response(f"Voice report: {data['report_type']}"),
                    'generated_at': 'now'
                }

            if report_data:
                report_obj = VoiceReport.objects.create(
                    ai_result=ai_result,
                    report_type=data['report_type'],
                    property_obj_id=data.get('property_id'),
                    report_text=report_data.get('report_text'),
                    report_audio_url=report_data.get('audio_url'),
                    key_highlights=report_data.get('key_highlights', []),
                    urgent_items=report_data.get('urgent_items', []),
                    recommended_actions=report_data.get('recommended_actions', []),
                )

                ai_result.status = "completed"
                ai_result.generated_content = report_data.get('report_text')
                ai_result.save()

                serializer = VoiceReportSerializer(report_obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                ai_result.status = "failed"
                ai_result.error_message = "AI voice report generation failed"
                ai_result.save()

                return Response(
                    {"error": "Could not generate voice report. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Error generating voice report: {e}")
            ai_result.status = "failed"
            ai_result.error_message = str(e)
            ai_result.save()

            return Response(
                {"error": "Failed to generate voice report. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_user_context(self, user, additional_context):
        """Get user context for voice interactions."""
        context = dict(additional_context)

        # Add user's managed properties
        try:
            from properties.models import Property
            if hasattr(user, 'user_type') and user.user_type == 'property_manager':
                properties = Property.objects.filter(
                    owner=user
                ) | Property.objects.filter(
                    managers=user
                )
                context['properties'] = [
                    {'id': p.id, 'name': p.name, 'address': p.address}
                    for p in properties[:5]  # Limit to 5 for context
                ]
        except Exception:
            pass

        # Add recent activities (placeholder)
        context['recent_activities'] = [
            "Checked property status",
            "Reviewed maintenance requests",
            "Generated financial report"
        ]

        from django.utils import timezone
        context['current_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        return context

    def _execute_voice_intent(self, intent, parameters, user):
        """Execute detected voice intent."""
        try:
            if intent == 'property_info' and parameters.get('property_id'):
                from properties.models import Property
                property_obj = Property.objects.get(id=parameters['property_id'])
                return {
                    'action': 'property_info_retrieved',
                    'result': {
                        'property_name': property_obj.name,
                        'address': property_obj.address,
                        'occupancy_rate': f"{(property_obj.get_occupancy_rate() or 0):.1f}%"
                    }
                }

            elif intent == 'maintenance_status':
                from maintenance.models import MaintenanceRequest
                urgent_count = MaintenanceRequest.objects.filter(
                    property__owner=user,
                    priority='emergency',
                    status__in=['pending', 'in_progress']
                ).count()
                return {
                    'action': 'maintenance_status_checked',
                    'result': {'urgent_requests': urgent_count}
                }

            elif intent == 'occupancy_report':
                from properties.models import Property
                properties = Property.objects.filter(owner=user)
                total_units = sum(p.total_units for p in properties)
                occupied_units = sum(
                    len([l for l in p.lease_set.filter(
                        lease_start_date__lte=timezone.now().date(),
                        lease_end_date__gte=timezone.now().date(),
                        status='active'
                    )]) for p in properties
                )
                occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
                return {
                    'action': 'occupancy_report_generated',
                    'result': {
                        'total_units': total_units,
                        'occupied_units': occupied_units,
                        'occupancy_rate': f"{occupancy_rate:.1f}%"
                    }
                }

        except Exception as e:
            logger.error(f"Error executing voice intent {intent}: {e}")

        return None

    def _gather_property_financial_data(self, property_obj, period):
        """Gather financial data for a property over the specified period."""
        from django.utils import timezone
        from datetime import timedelta
        from leases.models import Lease
        from payments.models import RentPayment
        from accounting.models import FinancialTransaction

        # Calculate date range
        end_date = timezone.now().date()
        if period == '3_months':
            start_date = end_date - timedelta(days=90)
        elif period == '6_months':
            start_date = end_date - timedelta(days=180)
        elif period == '24_months':
            start_date = end_date - timedelta(days=730)
        else:  # 12_months
            start_date = end_date - timedelta(days=365)

        # Gather rental income
        rental_income = RentPayment.objects.filter(
            lease__property_obj=property_obj,
            payment_date__range=[start_date, end_date],
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        # Gather expenses
        expenses = FinancialTransaction.objects.filter(
            property_obj=property_obj,
            transaction_date__range=[start_date, end_date],
            transaction_type__in=['expense', 'maintenance']
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        # Current occupancy
        active_leases = Lease.objects.filter(
            property_obj=property_obj,
            lease_start_date__lte=end_date,
            lease_end_date__gte=end_date,
            status='active'
        ).count()

        occupancy_rate = (active_leases / property_obj.total_units * 100) if property_obj.total_units > 0 else 0

        return {
            'property_info': {
                'name': property_obj.name,
                'address': property_obj.address,
                'total_units': property_obj.total_units,
                'year_built': property_obj.year_built,
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'months': (end_date - start_date).days // 30
            },
            'financials': {
                'rental_income': float(rental_income),
                'total_expenses': float(expenses),
                'net_operating_income': float(rental_income - expenses),
                'occupancy_rate': occupancy_rate,
            },
            'occupancy': {
                'current_occupied_units': active_leases,
                'total_units': property_obj.total_units,
                'occupancy_percentage': occupancy_rate,
            }
        }

    def _gather_comprehensive_property_data(self, property_obj):
        """Gather comprehensive property data for detailed reports."""
        financial_data = self._gather_property_financial_data(property_obj, '12_months')

        # Add additional property details
        financial_data.update({
            'management_info': {
                'managed_since': getattr(property_obj, 'acquisition_date', None),
                'management_fees': getattr(property_obj, 'management_fee_percentage', 0),
            },
            'market_info': {
                'location': property_obj.city + ', ' + property_obj.state if hasattr(property_obj, 'city') else 'Unknown',
                'property_type': property_obj.property_type,
            }
        })

        return financial_data

    def _parse_cost_range(self, cost_string: str, range_type: str) -> Optional[float]:
        """Parse cost range string like '$100-500' into min/max values."""
        if not cost_string:
            return None

        try:
            # Remove currency symbols and split on common separators
            cost_string = cost_string.replace('$', '').replace(',', '').strip()

            if '-' in cost_string:
                parts = cost_string.split('-')
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return min_val if range_type == 'min' else max_val
            elif cost_string.replace('.', '').isdigit():
                return float(cost_string)

        except (ValueError, AttributeError):
            pass

        return None