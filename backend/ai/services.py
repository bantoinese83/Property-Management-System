"""
AI Services for TenantBase - Property Management System
Integrates Google Gemini API for document processing, text generation, and intelligent automation.
"""

import os
import json
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


class PropertyInspectionService(GeminiAIService):
    """Service for analyzing property inspection photos and assessing damage."""

    def analyze_property_image(self, image_description: str, inspection_context: str = "") -> Optional[Dict[str, Any]]:
        """
        Analyze a property inspection image and provide assessment.

        Args:
            image_description: Description of what's in the image
            inspection_context: Additional context about the inspection

        Returns:
            Dictionary with image analysis results
        """
        prompt = f"""
        Analyze this property inspection image and provide a detailed assessment in JSON format:

        {{
            "overall_condition": "excellent/good/fair/poor/critical",
            "damage_assessment": "Description of any visible damage or issues",
            "maintenance_needed": "List of maintenance items identified",
            "safety_concerns": "Any safety issues or hazards detected",
            "estimated_costs": "Rough cost estimates for any repairs needed",
            "urgency_level": "low/medium/high/emergency",
            "recommendations": "Specific recommendations for property manager",
            "compliance_notes": "Any code compliance or regulatory concerns",
            "confidence_score": "Confidence in assessment (0.0 to 1.0)"
        }}

        Image Description: {image_description}
        Inspection Context: {inspection_context}

        Focus on structural integrity, habitability, safety, and maintenance needs.
        Be specific about locations, severity, and recommended actions.
        Return only valid JSON.
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.2,
            max_tokens=1000
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
            logger.error(f"Failed to parse property inspection analysis: {e}")
            return None

    def compare_before_after_images(self, before_description: str, after_description: str, work_description: str) -> Optional[Dict[str, Any]]:
        """
        Compare before and after images of property work.

        Args:
            before_description: Description of the before image
            after_description: Description of the after image
            work_description: Description of the work performed

        Returns:
            Comparison analysis results
        """
        prompt = f"""
        Compare before and after images of property maintenance/repair work and provide assessment in JSON format:

        {{
            "work_completion_quality": "excellent/good/satisfactory/poor/incomplete",
            "issues_resolved": "List of issues that appear to be fixed",
            "remaining_issues": "Any remaining problems or incomplete work",
            "quality_assessment": "Assessment of workmanship quality",
            "compliance_check": "Whether work appears to meet standards",
            "recommendations": "Any follow-up work or monitoring needed",
            "cost_accuracy": "Assessment of whether work matches described scope",
            "safety_improvement": "Safety improvements achieved",
            "confidence_score": "Confidence in assessment (0.0 to 1.0)"
        }}

        Before Image: {before_description}
        After Image: {after_description}
        Work Description: {work_description}

        Be thorough and objective in your assessment.
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
            logger.error(f"Failed to parse before/after comparison: {e}")
            return None


class VoiceAssistantService(GeminiAIService):
    """Service for voice-powered property management assistant using Live API."""

    def __init__(self):
        super().__init__()
        # Note: Live API would require websockets and real-time audio processing
        # This is a placeholder for future implementation with Live API
        self.live_api_available = False

    def process_voice_command(self, audio_transcript: str, user_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process voice commands for property management tasks.

        Args:
            audio_transcript: Transcribed voice input
            user_context: User context (properties managed, recent activities, etc.)

        Returns:
            Response with action to take and voice response
        """
        prompt = f"""
        You are TenantBase Assistant, an AI voice assistant for property managers.
        Process this voice command and determine the appropriate action.

        User Context:
        - Managed Properties: {user_context.get('properties', [])}
        - Recent Activities: {user_context.get('recent_activities', [])}
        - Current Time: {user_context.get('current_time', 'Unknown')}

        Voice Command: "{audio_transcript}"

        Analyze the command and provide:
        1. The intent/action the user wants to perform
        2. Required parameters or data needed
        3. A natural voice response to confirm/ask for clarification
        4. Any follow-up actions or questions

        Available Actions:
        - property_info: Get information about a specific property
        - tenant_info: Get information about a tenant
        - maintenance_status: Check maintenance request status
        - financial_summary: Get financial summary
        - schedule_inspection: Schedule a property inspection
        - create_task: Create a new task or reminder
        - occupancy_report: Get occupancy report
        - rent_due: Check upcoming rent payments

        Return in JSON format:
        {{
            "intent": "detected_action",
            "confidence": 0.0-1.0,
            "parameters": {{"key": "value"}},
            "response_text": "Natural voice response",
            "needs_clarification": false,
            "clarification_question": "if needed",
            "suggested_actions": ["follow_up_actions"]
        }}
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.3,
            max_tokens=1000
        )

        if not response:
            return None

        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)

                # Add voice response audio generation (placeholder for now)
                result['audio_response_url'] = self._generate_audio_response(result.get('response_text', ''))

                return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse voice command analysis: {e}")
            return None

    def generate_property_report_voice(self, property_id: int, user_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a voice property report for hands-free consumption.

        Args:
            property_id: ID of the property
            user_context: User context information

        Returns:
            Voice report data with audio URL
        """
        prompt = f"""
        Generate a concise voice property report for property manager. Keep it under 200 words.

        Property ID: {property_id}
        User Context: {user_context}

        Cover:
        1. Current occupancy status
        2. Financial highlights (rent collected, expenses)
        3. Active maintenance requests
        4. Upcoming events (lease renewals, inspections)
        5. Any urgent issues requiring attention

        Make it conversational and actionable, suitable for voice playback.
        Focus on key metrics and actionable insights.
        """

        report_text = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=400
        )

        if report_text:
            return {
                'report_text': report_text,
                'audio_url': self._generate_audio_response(report_text),
                'generated_at': 'now',
                'property_id': property_id
            }

        return None

    def _generate_audio_response(self, text: str) -> Optional[str]:
        """
        Generate audio response from text (placeholder for future TTS integration).

        In a full implementation, this would use Google's Text-to-Speech API
        or another TTS service to convert the response text to audio.

        Returns:
            URL to generated audio file or None
        """
        # Placeholder - would integrate with Google Cloud Text-to-Speech
        # or similar service in production
        if not text:
            return None

        # For now, return a placeholder URL
        # In production, this would generate and store actual audio
        return f"/api/audio/generated/{hash(text)}.mp3"


class FinancialAnalysisService(GeminiAIService):
    """Service for financial analysis and forecasting using AI."""

    def analyze_property_financials(self, financial_data: Dict[str, Any], analysis_period: str = "12_months") -> Optional[Dict[str, Any]]:
        """
        Analyze property financial performance and provide insights.

        Args:
            financial_data: Dictionary containing financial metrics
            analysis_period: Period for analysis (3_months, 6_months, 12_months, etc.)

        Returns:
            Dictionary with financial analysis and recommendations
        """
        prompt = f"""
        Analyze this property's financial performance and provide insights in JSON format:

        {{
            "profitability_assessment": "excellent/good/fair/poor",
            "key_financial_ratios": {{
                "occupancy_rate": "Current occupancy percentage",
                "noi_margin": "Net Operating Income margin",
                "cap_rate": "Capitalization rate if available",
                "cash_flow_stability": "Assessment of cash flow consistency"
            }},
            "trend_analysis": {{
                "revenue_trend": "increasing/stable/declining",
                "expense_trend": "increasing/stable/declining",
                "profit_trend": "increasing/stable/declining",
                "concerning_trends": "List of concerning financial trends"
            }},
            "forecast_12_months": {{
                "expected_revenue": "Projected annual revenue",
                "expected_expenses": "Projected annual expenses",
                "expected_profit": "Projected annual profit",
                "confidence_level": "high/medium/low"
            }},
            "recommendations": [
                "Specific recommendations for improving financial performance"
            ],
            "risk_assessment": {{
                "financial_risks": "Identified financial risks",
                "mitigation_strategies": "Strategies to address risks",
                "opportunity_areas": "Areas for financial improvement"
            }},
            "benchmarking_insights": "How this property compares to market averages",
            "confidence_score": "Confidence in analysis (0.0 to 1.0)"
        }}

        Financial Data for {analysis_period}:
        {json.dumps(financial_data, indent=2)}

        Provide data-driven insights based on standard real estate financial analysis principles.
        Return only valid JSON.
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
            logger.error(f"Failed to parse financial analysis: {e}")
            return None

    def generate_financial_report(self, property_data: Dict[str, Any], report_type: str = "monthly") -> Optional[str]:
        """
        Generate a comprehensive financial report using AI.

        Args:
            property_data: Property and financial data
            report_type: Type of report (monthly, quarterly, annual)

        Returns:
            Formatted financial report
        """
        prompt = f"""
        Generate a comprehensive {report_type} financial report for this property. Include:

        1. EXECUTIVE SUMMARY
           - Overall financial performance
           - Key highlights and concerns
           - Recommendations for action

        2. REVENUE ANALYSIS
           - Rental income breakdown
           - Occupancy trends
           - Revenue projections

        3. EXPENSE ANALYSIS
           - Major expense categories
           - Cost trends and variances
           - Budget vs actual performance

        4. PROFITABILITY METRICS
           - Net Operating Income (NOI)
           - Cash flow analysis
           - Return on investment metrics

        5. KEY PERFORMANCE INDICATORS
           - Occupancy rates
           - Collection rates
           - Expense ratios
           - Cash-on-cash returns

        6. FORECASTS AND PROJECTIONS
           - Short-term financial outlook
           - Market condition impact
           - Recommended adjustments

        7. RISK ASSESSMENT
           - Financial vulnerabilities
           - Market risks
           - Mitigation strategies

        8. RECOMMENDATIONS
           - Immediate actions needed
           - Long-term strategic improvements
           - Operational efficiencies

        Format as a professional financial report with clear sections and actionable insights.

        Property Data:
        {json.dumps(property_data, indent=2)}
        """

        return self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.3,
            max_tokens=2500
        )

    def analyze_investment_opportunity(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a property as an investment opportunity.

        Args:
            property_data: Property financial and operational data
            market_data: Local market conditions and comparables

        Returns:
            Investment analysis and recommendations
        """
        prompt = f"""
        Perform a comprehensive investment analysis for this property in JSON format:

        {{
            "investment_rating": "excellent/good/fair/poor/high_risk",
            "financial_projections": {{
                "year_1_noi": "Projected Net Operating Income",
                "year_3_noi": "3-year NOI projection",
                "cap_rate": "Current capitalization rate",
                "irr": "Internal Rate of Return estimate",
                "cash_on_cash": "Cash-on-cash return percentage"
            }},
            "market_analysis": {{
                "location_rating": "excellent/good/fair/poor",
                "market_trends": "Current market conditions and trends",
                "competitive_position": "How this property compares to competition",
                "growth_potential": "Future appreciation potential"
            }},
            "risk_assessment": {{
                "overall_risk": "low/medium/high",
                "specific_risks": ["List of specific investment risks"],
                "risk_mitigation": ["Strategies to mitigate identified risks"]
            }},
            "acquisition_strategy": {{
                "recommended_price_range": "Suggested acquisition price range",
                "negotiation_points": ["Key negotiation points"],
                "due_diligence_priorities": ["Critical due diligence items"]
            }},
            "value_add_opportunities": [
                "Potential improvements to increase property value"
            ],
            "exit_strategy": {{
                "hold_period": "Recommended holding period",
                "exit_options": ["Potential exit strategies"],
                "expected_returns": "Projected returns at exit"
            }},
            "confidence_score": "Confidence in analysis (0.0 to 1.0)"
        }}

        Property Data:
        {json.dumps(property_data, indent=2)}

        Market Data:
        {json.dumps(market_data, indent=2)}

        Base analysis on real estate investment principles and current market conditions.
        Return only valid JSON.
        """

        response = self.generate_content(
            prompt=prompt,
            model="gemini-2.5-pro",
            temperature=0.2,
            max_tokens=2000
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
            logger.error(f"Failed to parse investment analysis: {e}")
            return None


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
inspection_service = PropertyInspectionService()
financial_service = FinancialAnalysisService()
voice_service = VoiceAssistantService()