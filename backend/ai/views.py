"""
AI Views for TenantBase
API endpoints for AI-powered document processing, analysis, and communication generation.
"""

import logging
from typing import Optional, Dict, Any

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    AIProcessingResult,
    LeaseAnalysis,
    TenantApplicationAnalysis,
    MaintenanceAnalysis
)
from .serializers import (
    AIProcessingResultSerializer,
    LeaseAnalysisSerializer,
    TenantApplicationAnalysisSerializer,
    MaintenanceAnalysisSerializer,
    DocumentAnalysisRequestSerializer,
    MaintenanceAnalysisRequestSerializer,
    CommunicationRequestSerializer
)
from .services import (
    document_service,
    communication_service,
    maintenance_service
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