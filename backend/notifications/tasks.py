import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from leases.models import Lease
from maintenance.models import MaintenanceRequest
from payments.models import RentPayment
from users.models import Notification, NotificationPreference

from .services import EmailService

logger = logging.getLogger(__name__)


@shared_task
def send_rent_due_reminders():
    """Send rent payment due reminders"""
    today = timezone.now().date()
    reminder_date = today + timedelta(days=settings.NOTIFICATION_DAYS_BEFORE_DUE)

    # Get payments due in the notification window
    upcoming_payments = RentPayment.objects.filter(
        due_date=reminder_date, status__in=["pending", "overdue"]
    ).select_related("lease_obj", "lease_obj__tenant", "lease_obj__property_obj")

    sent_count = 0
    for payment in upcoming_payments:
        tenant = payment.lease_obj.tenant
        if not tenant:
            continue

        # Check tenant's notification preferences
        try:
            prefs = tenant.notification_preferences
            if not prefs.email_enabled or not prefs.email_payment_reminders:
                continue
        except NotificationPreference.DoesNotExist:
            # Default to sending if no preferences set
            pass

        # Send email reminder
        success = EmailService.send_rent_due_reminder(
            tenant_email=tenant.email,
            tenant_name=tenant.full_name,
            property_name=payment.lease_obj.property_obj.property_name,
            amount=str(payment.total_amount),
            due_date=payment.due_date.strftime("%B %d, %Y"),
            lease_period=f"{payment.lease_obj.lease_start_date.strftime('%B %Y')} - {payment.lease_obj.lease_end_date.strftime('%B %Y')}",
        )

        if success:
            sent_count += 1

            # Create in-app notification
            Notification.objects.create(
                user=tenant,
                notification_type="payment",
                title="Rent Payment Due Soon",
                message=f'Your rent payment of ${payment.total_amount} for {payment.lease_obj.property_obj.property_name} is due on {payment.due_date.strftime("%B %d, %Y")}.',
                related_model="payment",
                related_id=payment.id,
                action_url=f"/payments/{payment.id}",
            )

    logger.info(f"Sent {sent_count} rent due reminders")
    return sent_count


@shared_task
def send_maintenance_updates():
    """Send maintenance request updates to tenants"""
    today = timezone.now().date()

    # Get maintenance requests that need updates
    maintenance_requests = (
        MaintenanceRequest.objects.filter(tenant__isnull=False, status__in=["assigned", "in_progress", "completed"])
        .exclude(
            # Don't send updates for requests updated in the last 24 hours
            updated_at__gte=timezone.now()
            - timedelta(hours=24)
        )
        .select_related("tenant", "property_obj", "assigned_to")
    )

    sent_count = 0
    for request in maintenance_requests:
        tenant = request.tenant
        if not tenant:
            continue

        # Check tenant's notification preferences
        try:
            prefs = tenant.notification_preferences
            if not prefs.email_enabled or not prefs.email_maintenance_updates:
                continue
        except NotificationPreference.DoesNotExist:
            pass

        # Send email update
        success = EmailService.send_maintenance_update(
            tenant_email=tenant.email,
            tenant_name=tenant.full_name,
            property_name=request.property_obj.property_name,
            request_title=request.title,
            request_description=request.description,
            priority=request.priority,
            status=request.status,
            requested_date=request.requested_date.strftime("%B %d, %Y"),
            scheduled_date=request.scheduled_date.strftime("%B %d, %Y") if request.scheduled_date else None,
            estimated_cost=str(request.estimated_cost) if request.estimated_cost else None,
            actual_cost=str(request.actual_cost) if request.actual_cost else None,
            notes=request.notes,
        )

        if success:
            sent_count += 1

            # Create in-app notification
            status_messages = {
                "assigned": f'Your maintenance request "{request.title}" has been assigned and scheduled.',
                "in_progress": f'Work has begun on your maintenance request "{request.title}".',
                "completed": f'Your maintenance request "{request.title}" has been completed.',
            }

            Notification.objects.create(
                user=tenant,
                notification_type="maintenance",
                title="Maintenance Request Update",
                message=status_messages.get(request.status, f'Update on maintenance request "{request.title}"'),
                priority=request.priority,
                related_model="maintenance",
                related_id=request.id,
                action_url=f"/maintenance/{request.id}",
            )

    logger.info(f"Sent {sent_count} maintenance updates")
    return sent_count


@shared_task
def send_lease_expiration_reminders():
    """Send lease expiration reminders"""
    today = timezone.now().date()
    reminder_date = today + timedelta(days=settings.NOTIFICATION_DAYS_BEFORE_LEASE_END)

    # Get leases expiring in the notification window
    expiring_leases = Lease.objects.filter(lease_end_date=reminder_date, status="active").select_related(
        "tenant", "property_obj"
    )

    sent_count = 0
    for lease in expiring_leases:
        tenant = lease.tenant
        if not tenant:
            continue

        # Check tenant's notification preferences
        try:
            prefs = tenant.notification_preferences
            if not prefs.email_enabled or not prefs.email_lease_updates:
                continue
        except NotificationPreference.DoesNotExist:
            pass

        days_remaining = (lease.lease_end_date - today).days

        # Send email reminder
        success = EmailService.send_lease_expiration_reminder(
            tenant_email=tenant.email,
            tenant_name=tenant.full_name,
            property_name=lease.property_obj.property_name,
            lease_start_date=lease.lease_start_date.strftime("%B %d, %Y"),
            lease_end_date=lease.lease_end_date.strftime("%B %d, %Y"),
            monthly_rent=str(lease.monthly_rent),
            days_remaining=days_remaining,
            auto_renew=lease.auto_renew,
        )

        if success:
            sent_count += 1

            # Create in-app notification
            Notification.objects.create(
                user=tenant,
                notification_type="lease",
                title="Lease Expiration Notice",
                message=f'Your lease for {lease.property_obj.property_name} expires in {days_remaining} days on {lease.lease_end_date.strftime("%B %d, %Y")}.',
                priority="high" if days_remaining <= 30 else "medium",
                related_model="lease",
                related_id=lease.id,
                action_url=f"/leases/{lease.id}",
            )

    logger.info(f"Sent {sent_count} lease expiration reminders")
    return sent_count


@shared_task
def send_overdue_payment_alerts():
    """Send alerts for overdue payments"""
    today = timezone.now().date()

    # Get overdue payments
    overdue_payments = RentPayment.objects.filter(due_date__lt=today, status__in=["pending", "overdue"]).select_related(
        "lease_obj", "lease_obj__tenant", "lease_obj__property_obj"
    )

    sent_count = 0
    for payment in overdue_payments:
        tenant = payment.lease_obj.tenant
        if not tenant:
            continue

        # Only send if we haven't sent an alert in the last 7 days
        recent_alert = Notification.objects.filter(
            user=tenant,
            notification_type="payment",
            title__icontains="overdue",
            created_at__gte=timezone.now() - timedelta(days=7),
        ).exists()

        if recent_alert:
            continue

        # Check tenant's notification preferences
        try:
            prefs = tenant.notification_preferences
            if not prefs.email_enabled or not prefs.email_payment_reminders:
                continue
        except NotificationPreference.DoesNotExist:
            pass

        # Send email alert
        success = EmailService.send_rent_due_reminder(
            tenant_email=tenant.email,
            tenant_name=tenant.full_name,
            property_name=payment.lease_obj.property_obj.property_name,
            amount=str(payment.total_amount),
            due_date=payment.due_date.strftime("%B %d, %Y"),
            lease_period=f"{payment.lease_obj.lease_start_date.strftime('%B %Y')} - {payment.lease_obj.lease_end_date.strftime('%B %Y')}",
        )

        if success:
            sent_count += 1

            # Create in-app notification
            days_overdue = (today - payment.due_date).days
            Notification.objects.create(
                user=tenant,
                notification_type="payment",
                title="Payment Overdue",
                message=f'Your rent payment of ${payment.total_amount} for {payment.lease_obj.property_obj.property_name} was due on {payment.due_date.strftime("%B %d, %Y")} and is {days_overdue} days overdue.',
                priority="urgent",
                related_model="payment",
                related_id=payment.id,
                action_url=f"/payments/{payment.id}",
            )

    logger.info(f"Sent {sent_count} overdue payment alerts")
    return sent_count


@shared_task
def send_admin_summary_report():
    """Send daily summary report to administrators"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Get admin users
    admin_users = NotificationPreference.objects.filter(user__user_type="admin", email_enabled=True).select_related(
        "user"
    )

    if not admin_users.exists():
        return 0

    # Collect summary data
    summary_data = {
        "date": yesterday.strftime("%B %d, %Y"),
        "total_properties": 0,
        "active_leases": 0,
        "pending_maintenance": 0,
        "overdue_payments": 0,
        "total_collections": 0,
        "new_tenants": 0,
        "expiring_leases": 0,
    }

    # Get summary stats (simplified version - would need proper aggregation)
    from leases.models import Lease
    from maintenance.models import MaintenanceRequest
    from payments.models import RentPayment
    from properties.models import Property
    from tenants.models import Tenant

    summary_data["total_properties"] = Property.objects.count()
    summary_data["active_leases"] = Lease.objects.filter(status="active").count()
    summary_data["pending_maintenance"] = MaintenanceRequest.objects.filter(status__in=["open", "assigned"]).count()
    summary_data["overdue_payments"] = RentPayment.objects.filter(status="overdue").count()
    summary_data["new_tenants"] = Tenant.objects.filter(created_at__date=yesterday).count()
    summary_data["expiring_leases"] = Lease.objects.filter(
        lease_end_date__lte=today + timedelta(days=30), status="active"
    ).count()

    # Get yesterday's collections
    yesterday_payments = RentPayment.objects.filter(payment_date=yesterday, status="paid")
    summary_data["total_collections"] = sum(float(p.amount) for p in yesterday_payments)

    # Send email to admins
    admin_emails = [admin.user.email for admin in admin_users]
    subject = f'Daily Summary Report - {yesterday.strftime("%B %d, %Y")}'

    message = f"""
Daily Property Management Summary - {yesterday.strftime('%B %d, %Y')}

📊 OVERVIEW
• Total Properties: {summary_data['total_properties']}
• Active Leases: {summary_data['active_leases']}
• Pending Maintenance: {summary_data['pending_maintenance']}

💰 FINANCIAL
• Yesterday's Collections: ${summary_data['total_collections']:.2f}
• Overdue Payments: {summary_data['overdue_payments']}

👥 TENANTS
• New Tenants: {summary_data['new_tenants']}
• Expiring Leases (30 days): {summary_data['expiring_leases']}

This report was generated automatically by the Property Management System.
"""

    success = EmailService.send_system_notification(recipient_emails=admin_emails, subject=subject, message=message)

    if success:
        logger.info(f"Daily summary report sent to {len(admin_emails)} administrators")
        return len(admin_emails)

    return 0
