from celery import shared_task
from django.utils import timezone

from core.notifications import notify_lease_expiry

from .models import Lease


@shared_task
def check_lease_expiries():
    """
    Check for leases that are expiring soon and send notifications.
    This task should run once a day.
    """
    today = timezone.now().date()

    # We want to notify at specific intervals before expiry
    # For example: 60, 30, 15, and 7 days before
    intervals = [60, 30, 15, 7]

    for interval in intervals:
        expiry_date = today + timezone.timedelta(days=interval)
        leases = Lease.objects.filter(lease_end_date=expiry_date, status="active")

        for lease in leases:
            notify_lease_expiry(lease)

    # Also notify on the day of expiry
    expiring_today = Lease.objects.filter(lease_end_date=today, status="active")
    for lease in expiring_today:
        notify_lease_expiry(lease)
        # The save() method will handle updating status to 'expired' when called
        # but we might want to trigger it explicitly if no one visits the site
        lease.save()

    return f"Processed lease expiries for {today}"
