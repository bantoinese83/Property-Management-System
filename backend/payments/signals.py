from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.notifications import notify_payment_received

from .models import RentPayment


@receiver(post_save, sender=RentPayment)
def payment_notification(sender, instance, created, **kwargs):
    """
    Signal to send notification when a payment is created or status changes to 'paid'.
    """
    if created or (
        hasattr(instance, "_previous_status") and instance.status == "paid" and instance._previous_status != "paid"
    ):
        notify_payment_received(instance)


# We need a way to track the previous status for status changes
@receiver(pre_save, sender=RentPayment)
def track_payment_status(sender, instance, **kwargs):
    if instance.id:
        try:
            instance._previous_status = RentPayment.objects.get(id=instance.id).status
        except RentPayment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None
