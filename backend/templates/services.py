import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.template import Context, Template
from django.utils import timezone

from .models import DocumentTemplate, GeneratedDocument


class TemplateService:
    """Service for document template processing and generation"""

    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract variable names from template content"""
        # Find all {{variable}} patterns
        pattern = r"\{\{\s*(\w+)\s*\}\}"
        matches = re.findall(pattern, content)
        return list(set(matches))  # Remove duplicates

    @staticmethod
    def validate_template(content: str) -> Dict[str, Any]:
        """Validate template content and extract metadata"""
        variables = TemplateService.extract_variables(content)

        issues = []

        # Check for common issues
        if not content.strip():
            issues.append("Template content is empty")

        # Check for unmatched braces
        open_braces = content.count("{{")
        close_braces = content.count("}}")
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")

        return {
            "variables": variables,
            "variable_count": len(variables),
            "is_valid": len(issues) == 0,
            "issues": issues,
        }

    @staticmethod
    def render_template(content: str, variables: Dict[str, Any]) -> str:
        """Render template with provided variables"""
        try:
            # Create Django template
            template = Template(content)
            context = Context(variables)

            # Add common context variables
            context.update(
                {
                    "current_date": timezone.now().date(),
                    "current_datetime": timezone.now(),
                    "company_name": getattr(settings, "COMPANY_NAME", "Property Management Company"),
                    "company_address": getattr(settings, "COMPANY_ADDRESS", ""),
                    "company_phone": getattr(settings, "COMPANY_PHONE", ""),
                    "company_email": getattr(settings, "COMPANY_EMAIL", ""),
                }
            )

            return template.render(context)
        except Exception as e:
            raise ValueError(f"Template rendering failed: {str(e)}")

    @staticmethod
    def generate_document(
        template_id: int,
        variables: Dict[str, Any],
        title: str,
        user,
        related_model: Optional[str] = None,
        related_id: Optional[int] = None,
    ) -> GeneratedDocument:
        """Generate a document from a template"""

        try:
            template = DocumentTemplate.objects.get(id=template_id, is_active=True)
        except DocumentTemplate.DoesNotExist:
            raise ValueError("Template not found or inactive")

        # Validate required variables
        template_vars = set(template.variables or [])
        provided_vars = set(variables.keys())

        missing_vars = template_vars - provided_vars
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

        # Render the document
        rendered_content = TemplateService.render_template(template.content, variables)

        # Create the document record
        document = GeneratedDocument.objects.create(
            title=title,
            template=template,
            content=template.content,  # Store original template
            variables_data=variables,
            generated_content=rendered_content,
            status="generated",
            related_model=related_model,
            related_id=related_id,
            created_by=user,
        )

        # Update template usage stats
        template.increment_usage()

        return document

    @staticmethod
    def get_template_variables(template: DocumentTemplate) -> Dict[str, Any]:
        """Get template variables with descriptions and defaults"""

        # Define common variable descriptions
        variable_descriptions = {
            "tenant_name": {"description": "Full name of the tenant", "type": "string"},
            "tenant_email": {"description": "Email address of the tenant", "type": "email"},
            "tenant_phone": {"description": "Phone number of the tenant", "type": "phone"},
            "tenant_address": {"description": "Current address of the tenant", "type": "address"},
            "property_name": {"description": "Name of the property", "type": "string"},
            "property_address": {"description": "Full address of the property", "type": "address"},
            "property_city": {"description": "City where property is located", "type": "string"},
            "property_state": {"description": "State where property is located", "type": "string"},
            "lease_start_date": {"description": "Lease start date", "type": "date"},
            "lease_end_date": {"description": "Lease end date", "type": "date"},
            "monthly_rent": {"description": "Monthly rent amount", "type": "currency"},
            "security_deposit": {"description": "Security deposit amount", "type": "currency"},
            "current_date": {"description": "Current date (auto-filled)", "type": "date", "auto": True},
            "company_name": {"description": "Company name (auto-filled)", "type": "string", "auto": True},
        }

        variables_info = {}
        for var_name in template.variables or []:
            variables_info[var_name] = variable_descriptions.get(
                var_name, {"description": f"Variable: {var_name}", "type": "string"}
            )

        return variables_info

    @staticmethod
    def create_default_templates():
        """Create default system templates"""

        templates_data = [
            {
                "name": "residential_lease_agreement",
                "display_name": "Residential Lease Agreement",
                "description": "Standard residential lease agreement template",
                "template_type": "lease",
                "category": "residential",
                "is_system_template": True,
                "content": """
RESIDENTIAL LEASE AGREEMENT

This Lease Agreement (the "Agreement") is made and entered into this {{ current_date }} day of {{ current_date|date:"F" }}, {{ current_date|date:"Y" }}, by and between:

LANDLORD: {{ company_name }}
Address: {{ company_address }}

TENANT: {{ tenant_name }}
Address: {{ tenant_address }}

PROPERTY: {{ property_name }}
Address: {{ property_address }}

LEASE TERM:
The lease term shall commence on {{ lease_start_date }} and end on {{ lease_end_date }}.

RENT:
Tenant agrees to pay Landlord the sum of ${{ monthly_rent }} per month, due on the 1st day of each month.

SECURITY DEPOSIT:
Tenant shall pay a security deposit of ${{ security_deposit }} upon execution of this Agreement.

SIGNATURES:

Landlord: _______________________________ Date: ____________

Tenant: _______________________________ Date: ____________
""",
            },
            {
                "name": "rent_payment_reminder",
                "display_name": "Rent Payment Reminder Notice",
                "description": "Notice for reminding tenants of upcoming or overdue rent payments",
                "template_type": "notice",
                "category": "payment",
                "is_system_template": True,
                "content": """
{{ company_name }}
{{ company_address }}

{{ current_date }}

{{ tenant_name }}
{{ tenant_address }}

RE: RENT PAYMENT REMINDER - {{ property_name }}

Dear {{ tenant_name }},

This is a reminder that your rent payment is due.

Property: {{ property_name }}
Amount Due: ${{ monthly_rent }}
Due Date: 1st of each month

Please ensure your payment is made by the due date to avoid late fees.

If you have already made this payment, please disregard this notice.

Thank you for your prompt attention.

Sincerely,

{{ company_name }}
{{ company_phone }}
{{ company_email }}
""",
            },
            {
                "name": "lease_termination_notice",
                "display_name": "Lease Termination Notice",
                "description": "Notice for lease termination or non-renewal",
                "template_type": "notice",
                "category": "termination",
                "is_system_template": True,
                "content": """
{{ company_name }}
{{ company_address }}

{{ current_date }}

{{ tenant_name }}
{{ tenant_address }}

NOTICE OF LEASE TERMINATION

Dear {{ tenant_name }},

This letter serves as formal notice that your lease agreement for the property located at {{ property_address }} will terminate on {{ lease_end_date }}.

Please make arrangements to vacate the premises by the termination date. The property should be left in the same condition as when you moved in, normal wear and tear excepted.

If you have any questions about this notice or the move-out process, please contact our office immediately.

Sincerely,

{{ company_name }}
Property Management
{{ company_phone }}
{{ company_email }}
""",
            },
        ]

        created_count = 0
        for template_data in templates_data:
            template, created = DocumentTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )

            if created:
                # Extract and set variables
                variables = TemplateService.extract_variables(template.content)
                template.variables = variables
                template.save()

                created_count += 1

        return created_count
