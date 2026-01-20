import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import AuditLog

logger = logging.getLogger(__name__)
User = get_user_model()

# Models to audit (exclude sensitive data models)
AUDITED_MODELS = [
    "properties.Property",
    "tenants.Tenant",
    "leases.Lease",
    "maintenance.MaintenanceRequest",
    "payments.RentPayment",
    "accounting.FinancialTransaction",
    "accounting.AccountingPeriod",
    "users.User",
    "users.UserProfile",
    "billing.SubscriptionPlan",
    "billing.Subscription",
    "billing.PaymentMethod",
    "billing.Invoice",
    "reports.Report",
]

# Fields to exclude from audit (sensitive data)
EXCLUDED_FIELDS = [
    "password",
    "secret_key",
    "api_key",
    "access_token",
    "refresh_token",
    "session_key",
]


def get_model_string(instance):
    """Get model string in format 'app.Model'"""
    return f"{instance._meta.app_label}.{instance._meta.model_name}"


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get("HTTP_USER_AGENT", "")


def serialize_instance(instance, exclude_fields=None):
    """Serialize model instance to dict, excluding specified fields"""
    if exclude_fields is None:
        exclude_fields = EXCLUDED_FIELDS

    data = {}
    for field in instance._meta.fields:
        if field.name not in exclude_fields:
            value = getattr(instance, field.name)
            # Convert datetime objects to ISO format
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[field.name] = value

    return data


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Store old values before save for update tracking"""
    if not instance.pk:  # New instance
        return

    model_string = get_model_string(instance)
    if model_string not in AUDITED_MODELS:
        return

    # Store old values in instance for post_save handler
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._audit_old_values = serialize_instance(old_instance)
    except sender.DoesNotExist:
        pass


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Create audit log for save operations"""
    model_string = get_model_string(instance)
    if model_string not in AUDITED_MODELS:
        return

    action = "create" if created else "update"
    action_description = f"{'Created' if created else 'Updated'} {model_string}"

    # Get user from thread local or instance
    user = getattr(instance, "_audit_user", None)

    # Get request context if available
    request = getattr(instance, "_audit_request", None)

    # Prepare audit data
    audit_data = {
        "content_type": ContentType.objects.get_for_model(instance),
        "object_id": instance.pk,
        "action": action,
        "action_description": action_description,
        "app_label": instance._meta.app_label,
        "model_name": instance._meta.model_name,
    }

    if user:
        audit_data["user"] = user
        audit_data["username"] = user.username
    else:
        audit_data["username"] = "system"

    if request:
        audit_data["ip_address"] = get_client_ip(request)
        audit_data["user_agent"] = get_user_agent(request)

    # For updates, include changed values
    if not created and hasattr(instance, "_audit_old_values"):
        new_values = serialize_instance(instance)
        old_values = getattr(instance, "_audit_old_values", {})

        # Only log if there are actual changes
        if old_values != new_values:
            audit_data["old_values"] = old_values
            audit_data["new_values"] = new_values

            # Create the audit log
            try:
                AuditLog.objects.create(**audit_data)
                logger.info(f"Audit log created: {action_description}")
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}")

    elif created:
        # For new objects, just log the creation
        audit_data["new_values"] = serialize_instance(instance)
        try:
            AuditLog.objects.create(**audit_data)
            logger.info(f"Audit log created: {action_description}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Create audit log for delete operations"""
    model_string = get_model_string(instance)
    if model_string not in AUDITED_MODELS:
        return

    action_description = f"Deleted {model_string}"

    # Get user from thread local
    user = getattr(instance, "_audit_user", None)
    request = getattr(instance, "_audit_request", None)

    audit_data = {
        "content_type": ContentType.objects.get_for_model(instance),
        "object_id": instance.pk,
        "action": "delete",
        "action_description": action_description,
        "old_values": serialize_instance(instance),
        "app_label": instance._meta.app_label,
        "model_name": instance._meta.model_name,
    }

    if user:
        audit_data["user"] = user
        audit_data["username"] = user.username
    else:
        audit_data["username"] = "system"

    if request:
        audit_data["ip_address"] = get_client_ip(request)
        audit_data["user_agent"] = get_user_agent(request)

    try:
        AuditLog.objects.create(**audit_data)
        logger.info(f"Audit log created: {action_description}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


@receiver(user_logged_in)
def audit_user_login(sender, request, user, **kwargs):
    """Audit user login events"""
    try:
        AuditLog.objects.create(
            user=user,
            username=user.username,
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.pk,
            action="login",
            action_description=f"User {user.username} logged in",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            app_label="users",
            model_name="user",
        )
        logger.info(f"Login audit log created for user: {user.username}")
    except Exception as e:
        logger.error(f"Failed to create login audit log: {e}")


@receiver(user_logged_out)
def audit_user_logout(sender, request, user, **kwargs):
    """Audit user logout events"""
    try:
        AuditLog.objects.create(
            user=user,
            username=user.username,
            content_type=ContentType.objects.get_for_model(user),
            object_id=user.pk,
            action="logout",
            action_description=f"User {user.username} logged out",
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else "",
            app_label="users",
            model_name="user",
        )
        logger.info(f"Logout audit log created for user: {user.username}")
    except Exception as e:
        logger.error(f"Failed to create logout audit log: {e}")


# Thread local storage for request context
import threading

local = threading.local()


def set_audit_context(user=None, request=None):
    """Set audit context for the current thread"""
    local.audit_user = user
    local.audit_request = request


def get_audit_context():
    """Get audit context for the current thread"""
    return {
        "user": getattr(local, "audit_user", None),
        "request": getattr(local, "audit_request", None),
    }


def with_audit_context(user=None, request=None):
    """Decorator to set audit context for a function"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            old_context = get_audit_context()
            set_audit_context(user, request)
            try:
                return func(*args, **kwargs)
            finally:
                set_audit_context(old_context["user"], old_context["request"])

        return wrapper

    return decorator
