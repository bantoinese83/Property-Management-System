from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_notification(subject, message, recipient_list, html_message=None):
    """
    Send an email notification.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Email notification sent to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        return False

def notify_maintenance_request(request_obj):
    """
    Notify relevant parties about a new maintenance request.
    """
    subject = f"New Maintenance Request: {request_obj.title}"
    message = f"A new maintenance request has been submitted for {request_obj.property_obj.property_name}.\n\n" \
              f"Description: {request_obj.description}\n" \
              f"Priority: {request_obj.priority}\n" \
              f"Submitted by: {request_obj.tenant.full_name if request_obj.tenant else 'Unknown'}"

    # In a real app, you'd find managers for this property
    # For now, we'll send to the property owner
    recipients = [request_obj.property_obj.owner.email]

    return send_email_notification(subject, message, recipients)

def notify_payment_received(payment_obj):
    """
    Notify relevant parties about a received payment.
    """
    subject = f"Payment Received: {payment_obj.amount} for {payment_obj.lease_obj.property_obj.property_name}"
    message = f"A payment has been received for {payment_obj.lease_obj.property_obj.property_name}.\n\n" \
              f"Amount: {payment_obj.amount}\n" \
              f"Payment Date: {payment_obj.payment_date}\n" \
              f"Status: {payment_obj.get_status_display()}\n" \
              f"Tenant: {payment_obj.lease_obj.tenant.full_name}"

    # Notify property owner
    recipients = [payment_obj.lease_obj.property_obj.owner.email]
    
    # Also notify tenant as a receipt
    if payment_obj.lease_obj.tenant.email:
        recipients.append(payment_obj.lease_obj.tenant.email)

    return send_email_notification(subject, message, recipients)

def notify_maintenance_status_change(request_obj):
    """
    Notify relevant parties about a status change in a maintenance request.
    """
    subject = f"Maintenance Update: {request_obj.title} is now {request_obj.get_status_display()}"
    message = f"The status of your maintenance request for {request_obj.property_obj.property_name} has been updated.\n\n" \
              f"Request: {request_obj.title}\n" \
              f"New Status: {request_obj.get_status_display()}\n" \
              f"Updated at: {request_obj.updated_at}\n\n" \
              f"Description: {request_obj.description}"

    recipients = []
    if request_obj.tenant and request_obj.tenant.email:
        recipients.append(request_obj.tenant.email)
    
    # Also notify owner of the change
    if request_obj.property_obj.owner.email not in recipients:
        recipients.append(request_obj.property_obj.owner.email)

    if not recipients:
        return False

    return send_email_notification(subject, message, recipients)

def notify_lease_expiry(lease_obj):
    """
    Notify relevant parties about an upcoming lease expiry.
    """
    subject = f"Lease Expiry Notice: {lease_obj.property_obj.property_name}"
    message = f"The lease for {lease_obj.property_obj.property_name} is set to expire on {lease_obj.lease_end_date}.\n\n" \
              f"Tenant: {lease_obj.tenant.full_name if lease_obj.tenant else 'N/A'}\n" \
              f"Days Remaining: {lease_obj.days_remaining}\n\n" \
              f"Please take necessary actions for renewal or move-out."

    recipients = [lease_obj.property_obj.owner.email]
    if lease_obj.tenant and lease_obj.tenant.email:
        recipients.append(lease_obj.tenant.email)

    return send_email_notification(subject, message, recipients)

def notify_lease_created(lease_obj):
    """
    Notify tenant about a new lease.
    """
    subject = f"New Lease Agreement: {lease_obj.property_obj.property_name}"
    message = f"A new lease agreement has been created for you at {lease_obj.property_obj.property_name}.\n\n" \
              f"Start Date: {lease_obj.lease_start_date}\n" \
              f"End Date: {lease_obj.lease_end_date}\n" \
              f"Monthly Rent: {lease_obj.monthly_rent}\n" \
              f"Security Deposit: {lease_obj.security_deposit}\n\n" \
              f"Please log in to the portal to view the full details and sign the agreement."

    recipients = []
    if lease_obj.tenant and lease_obj.tenant.email:
        recipients.append(lease_obj.tenant.email)
    
    if not recipients:
        return False

    return send_email_notification(subject, message, recipients)

def notify_payment_overdue(payment_obj):
    """
    Notify tenant about an overdue payment.
    """
    subject = f"OVERDUE PAYMENT: {payment_obj.lease_obj.property_obj.property_name}"
    message = f"Your rent payment for {payment_obj.lease_obj.property_obj.property_name} is overdue.\n\n" \
              f"Amount Due: {payment_obj.amount}\n" \
              f"Due Date: {payment_obj.due_date}\n" \
              f"Late Fee: {payment_obj.late_fee}\n" \
              f"Total Due: {payment_obj.total_amount}\n\n" \
              f"Please make the payment as soon as possible to avoid further late fees."

    recipients = []
    if payment_obj.lease_obj.tenant and payment_obj.lease_obj.tenant.email:
        recipients.append(payment_obj.lease_obj.tenant.email)
    
    if not recipients:
        return False

    return send_email_notification(subject, message, recipients)

def notify_rent_due(payment_obj):
    """
    Notify tenant that rent is due soon.
    """
    subject = f"Rent Due Reminder: {payment_obj.lease_obj.property_obj.property_name}"
    message = f"This is a reminder that your rent for {payment_obj.lease_obj.property_obj.property_name} is due on {payment_obj.due_date}.\n\n" \
              f"Amount: {payment_obj.amount}\n\n" \
              f"You can pay online through our portal."

    recipients = []
    if payment_obj.lease_obj.tenant and payment_obj.lease_obj.tenant.email:
        recipients.append(payment_obj.lease_obj.tenant.email)
    
    if not recipients:
        return False

    return send_email_notification(subject, message, recipients)
