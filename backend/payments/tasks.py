from celery import shared_task
from django.utils import timezone
from .models import RentPayment
from core.notifications import notify_payment_overdue, notify_rent_due

@shared_task
def check_payment_due_dates():
    """
    Check for payments that are due soon or overdue and send notifications.
    Runs daily.
    """
    today = timezone.now().date()
    
    # 1. Remind 3 days before due date
    three_days_from_now = today + timezone.timedelta(days=3)
    upcoming_payments = RentPayment.objects.filter(
        due_date=three_days_from_now,
        status='pending'
    )
    for payment in upcoming_payments:
        notify_rent_due(payment)
        
    # 2. Notify when payment becomes overdue (the day after due date)
    yesterday = today - timezone.timedelta(days=1)
    newly_overdue = RentPayment.objects.filter(
        due_date=yesterday,
        status='pending'
    )
    for payment in newly_overdue:
        payment.status = 'overdue'
        payment.save()
        notify_payment_overdue(payment)
        
    # 3. Weekly reminder for all overdue payments
    if today.weekday() == 0:  # Monday
        all_overdue = RentPayment.objects.filter(status='overdue')
        for payment in all_overdue:
            notify_payment_overdue(payment)

    return f"Processed payment notifications for {today}"
