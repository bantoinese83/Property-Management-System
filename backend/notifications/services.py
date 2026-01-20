import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending various types of email notifications"""

    @staticmethod
    def send_rent_due_reminder(
        tenant_email: str,
        tenant_name: str,
        property_name: str,
        amount: str,
        due_date: str,
        lease_period: str,
        payment_link: str = "#",
    ) -> bool:
        """Send rent payment due reminder"""
        try:
            context = {
                "tenant_name": tenant_name,
                "property_name": property_name,
                "amount": amount,
                "due_date": due_date,
                "lease_period": lease_period,
                "payment_link": payment_link,
                "company_name": getattr(settings, "COMPANY_NAME", "Property Management"),
                "contact_email": getattr(settings, "CONTACT_EMAIL", "contact@property-mgmt.com"),
                "contact_phone": getattr(settings, "CONTACT_PHONE", "(555) 123-4567"),
            }

            subject = f"Rent Payment Due Reminder - {property_name}"
            html_content = render_to_string("emails/rent_due_reminder.html", context)

            send_mail(
                subject=subject,
                message="",  # Plain text version could be added
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant_email],
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"Rent due reminder sent to {tenant_email} for {property_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send rent due reminder to {tenant_email}: {str(e)}")
            return False

    @staticmethod
    def send_maintenance_update(
        tenant_email: str,
        tenant_name: str,
        property_name: str,
        request_title: str,
        request_description: str,
        priority: str,
        status: str,
        requested_date: str,
        scheduled_date: Optional[str] = None,
        estimated_cost: Optional[str] = None,
        actual_cost: Optional[str] = None,
        notes: str = "",
    ) -> bool:
        """Send maintenance request update"""
        try:
            context = {
                "tenant_name": tenant_name,
                "property_name": property_name,
                "request_title": request_title,
                "request_description": request_description,
                "priority": priority.title(),
                "status": status.replace("_", " ").title(),
                "requested_date": requested_date,
                "scheduled_date": scheduled_date,
                "estimated_cost": estimated_cost,
                "actual_cost": actual_cost,
                "notes": notes,
                "company_name": getattr(settings, "COMPANY_NAME", "Property Management"),
                "contact_email": getattr(settings, "CONTACT_EMAIL", "contact@property-mgmt.com"),
                "contact_phone": getattr(settings, "CONTACT_PHONE", "(555) 123-4567"),
            }

            subject = f"Maintenance Update - {request_title}"
            html_content = render_to_string("emails/maintenance_reminder.html", context)

            send_mail(
                subject=subject,
                message="",  # Plain text version could be added
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant_email],
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"Maintenance update sent to {tenant_email} for {request_title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send maintenance update to {tenant_email}: {str(e)}")
            return False

    @staticmethod
    def send_lease_expiration_reminder(
        tenant_email: str,
        tenant_name: str,
        property_name: str,
        lease_start_date: str,
        lease_end_date: str,
        monthly_rent: str,
        days_remaining: int,
        auto_renew: bool = False,
        contact_link: str = "#",
        renewal_link: str = "#",
    ) -> bool:
        """Send lease expiration reminder"""
        try:
            context = {
                "tenant_name": tenant_name,
                "property_name": property_name,
                "lease_start_date": lease_start_date,
                "lease_end_date": lease_end_date,
                "monthly_rent": monthly_rent,
                "days_remaining": days_remaining,
                "auto_renew": auto_renew,
                "contact_link": contact_link,
                "renewal_link": renewal_link,
                "company_name": getattr(settings, "COMPANY_NAME", "Property Management"),
                "contact_email": getattr(settings, "CONTACT_EMAIL", "contact@property-mgmt.com"),
                "contact_phone": getattr(settings, "CONTACT_PHONE", "(555) 123-4567"),
            }

            subject = f"Lease Expiration Notice - {property_name}"
            html_content = render_to_string("emails/lease_expiration_reminder.html", context)

            send_mail(
                subject=subject,
                message="",  # Plain text version could be added
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[tenant_email],
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"Lease expiration reminder sent to {tenant_email} for {property_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send lease expiration reminder to {tenant_email}: {str(e)}")
            return False

    @staticmethod
    def send_system_notification(
        recipient_emails: List[str], subject: str, message: str, html_content: Optional[str] = None
    ) -> bool:
        """Send system notification (admin alerts, etc.)"""
        try:
            send_mail(
                subject=f"[System] {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                html_message=html_content,
                fail_silently=False,
            )

            logger.info(f"System notification sent to {len(recipient_emails)} recipients: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send system notification: {str(e)}")
            return False
