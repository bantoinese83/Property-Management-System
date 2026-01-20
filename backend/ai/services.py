"""
AI Services for TenantBase - Property Management System
Integrates Google Gemini API for document processing, text generation, and intelligent automation.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from django.conf import settings
from django.core.files.base import File
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiAIService:
    """Base service for Google Gemini AI integration."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI service: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None

    def generate_content(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Optional[str]:
        """Generate content using Gemini AI."""
        if not self.is_available():
            logger.warning("AI service not available - skipping content generation")
            return None

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini AI: {e}")
            return None


class DocumentProcessingService(GeminiAIService):
    """Service for processing documents using Gemini AI."""

    def extract_lease_data(self, document_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from lease agreements.

        Args:
            document_content: Text content of the lease document

        Returns:
            Dictionary with extracted lease data or None if extraction fails
        """
        prompt = f"""
        Analyze this lease agreement and extract the following information in JSON format:

        {{
            "tenant_name": "Full name of the tenant(s)",
            "property_address": "Complete property address",
            "monthly_rent": "Monthly rent amount as a number (remove currency symbols)",
            "lease_start_date": "Start date in YYYY-MM-DD format",
            "lease_end_date": "End date in YYYY-MM-DD format",
            "security_deposit": "Security deposit amount as a number",
            "pet_deposit": "Pet deposit if mentioned, otherwise null",
            "utilities_included": "List of utilities included in rent",
            "special_terms": "Any special terms or conditions",
            "confidence_score": "Confidence in extraction accuracy (0.0 to 1.0)"
        }}

        Lease document text:
        {document_content[:10000]}  # Limit to first 10k chars for API limits

        Return only valid JSON. If information is not available, use null values.
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.1,  # Low temperature for structured output
            max_tokens=2000
        )

        if not response:
            return None

        try:
            # Parse the JSON response
            import json
            # Clean the response to extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.error("Could not find JSON in AI response")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return None

    def analyze_tenant_application(self, application_content: str) -> Optional[Dict[str, Any]]:
        """
        Analyze tenant application and extract key information.

        Args:
            application_content: Text content of the tenant application

        Returns:
            Dictionary with application analysis or None if analysis fails
        """
        prompt = f"""
        Analyze this tenant rental application and extract key information in JSON format:

        {{
            "applicant_name": "Full name of the applicant",
            "current_address": "Current residential address",
            "phone_number": "Phone number",
            "email": "Email address",
            "employment_status": "Employment status (employed, self-employed, student, retired, etc.)",
            "monthly_income": "Monthly income as a number",
            "credit_score_mentioned": "Credit score if mentioned, otherwise null",
            "previous_landlord_info": "Information about previous landlord/references",
            "pets": "Information about pets (type, breed, size)",
            "move_in_timeline": "Desired move-in timeline",
            "rental_history": "Summary of rental history",
            "risk_assessment": "Overall risk assessment (low/medium/high)",
            "recommendations": "Any recommendations or concerns",
            "confidence_score": "Confidence in analysis (0.0 to 1.0)"
        }}

        Application text:
        {application_content[:8000]}

        Return only valid JSON. Use null for unavailable information.
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.2,
            max_tokens=1500
        )

        if not response:
            return None

        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tenant application analysis: {e}")
            return None

    def generate_lease_summary(self, lease_content: str) -> Optional[str]:
        """
        Generate a concise summary of lease terms for property managers.

        Args:
            lease_content: Full text of the lease agreement

        Returns:
            Concise summary of key lease terms
        """
        prompt = f"""
        Create a concise summary of this lease agreement highlighting the most important terms for a property manager:

        Focus on:
        - Tenant information
        - Property details
        - Financial terms (rent, deposits, fees)
        - Lease duration and renewal terms
        - Key responsibilities of tenant and landlord
        - Any special conditions or restrictions

        Keep the summary under 300 words and use clear, professional language.

        Lease text:
        {lease_content[:5000]}
        """

        return self.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=500
        )


class CommunicationService(GeminiAIService):
    """Service for generating automated communications."""

    def generate_tenant_welcome_email(self, tenant_name: str, property_address: str, move_in_date: str) -> Optional[str]:
        """Generate a personalized welcome email for new tenants."""
        prompt = f"""
        Write a professional welcome email for a new tenant moving into a rental property.

        Tenant Name: {tenant_name}
        Property Address: {property_address}
        Move-in Date: {move_in_date}

        Include:
        - Warm welcome and excitement about their move
        - Key move-in information and reminders
        - Contact information for questions
        - Brief overview of community rules
        - Professional and friendly tone

        Format as a complete email with subject line.
        """

        return self.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=600
        )

    def generate_maintenance_response(self, issue_description: str, priority: str, estimated_time: str) -> Optional[str]:
        """Generate a professional response to maintenance requests."""
        prompt = f"""
        Write a professional response to a tenant's maintenance request.

        Issue: {issue_description}
        Priority: {priority}
        Estimated Resolution Time: {estimated_time}

        Include:
        - Acknowledgment of the issue
        - Timeline for resolution
        - Next steps in the process
        - Contact information for follow-up
        - Reassurance about the resolution process

        Keep it concise and professional.
        """

        return self.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            temperature=0.6,
            max_tokens=400
        )


class MaintenanceAnalysisService(GeminiAIService):
    """Service for analyzing maintenance requests and prioritizing work."""

    def analyze_maintenance_request(self, description: str, urgency: str, property_type: str) -> Optional[Dict[str, Any]]:
        """
        Analyze maintenance request and provide recommendations.

        Args:
            description: Description of the maintenance issue
            urgency: Urgency level (low/medium/high/emergency)
            property_type: Type of property (apartment, house, etc.)

        Returns:
            Analysis with priority, cost estimate, and recommendations
        """
        prompt = f"""
        Analyze this maintenance request and provide recommendations in JSON format:

        {{
            "priority_assessment": "Assessed priority level (low/medium/high/emergency)",
            "estimated_cost": "Estimated cost range (e.g., '$100-500')",
            "required_skills": "Skills needed (plumbing, electrical, general, etc.)",
            "parts_needed": "Likely parts or materials required",
            "safety_concerns": "Any safety issues or hazards",
            "recommendations": "Suggested approach and timeline",
            "vendor_needed": "Whether specialized vendor is required",
            "follow_up_required": "Whether follow-up inspection is needed"
        }}

        Maintenance Request: {description}
        Reported Urgency: {urgency}
        Property Type: {property_type}

        Return only valid JSON.
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.2,
            max_tokens=800
        )

        if not response:
            return None

        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse maintenance analysis: {e}")
            return None


# Global service instances
document_service = DocumentProcessingService()
communication_service = CommunicationService()
maintenance_service = MaintenanceAnalysisService()