from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import MaintenanceRequest
from core.notifications import notify_maintenance_request, notify_maintenance_status_change

@receiver(post_save, sender=MaintenanceRequest)
def maintenance_request_notification(sender, instance, created, **kwargs):
    """
    Signal to send notification when a maintenance request is created or status changes.
    """
    if created:
        notify_maintenance_request(instance)
    elif hasattr(instance, '_previous_status') and instance.status != instance._previous_status:
        notify_maintenance_status_change(instance)

@receiver(pre_save, sender=MaintenanceRequest)
def track_maintenance_status(sender, instance, **kwargs):
    if instance.id:
        try:
            instance._previous_status = MaintenanceRequest.objects.get(id=instance.id).status
        except MaintenanceRequest.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None
