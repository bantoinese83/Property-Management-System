from django.db.models.signals import post_save
from django.dispatch import receiver

from core.notifications import notify_lease_created

from .models import Lease


@receiver(post_save, sender=Lease)
def lease_created_notification(sender, instance, created, **kwargs):
    """
    Signal to send notification when a new lease is created.
    """
    if created:
        notify_lease_created(instance)
