from rest_framework import permissions


class IsPropertyOwner(permissions.BasePermission):
    """Only property owner can edit/delete"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsPropertyOwnerOrReadOnly(permissions.BasePermission):
    """Owner has all permissions, others have read-only"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsTenantOrAdmin(permissions.BasePermission):
    """Tenant can only see own data"""

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        if hasattr(obj, "tenant"):
            return obj.tenant.id == request.user.id
        return False


class IsOwnerOrPropertyManager(permissions.BasePermission):
    """Allow owner or assigned property manager"""

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "property") and hasattr(obj.property, "owner"):
            return obj.property.owner == request.user
        return False


class IsLeaseTenantOrPropertyOwner(permissions.BasePermission):
    """Allow tenant or property owner to access lease"""

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        # Property owner can access
        if obj.property.owner == request.user:
            return True
        # Tenant can access their own leases
        if obj.tenant and obj.tenant.id == request.user.id:
            return True
        return False


class IsPaymentRelatedParty(permissions.BasePermission):
    """Allow parties related to payment (tenant, property owner, admin)"""

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        # Property owner can access payments for their properties
        if obj.lease.property.owner == request.user:
            return True
        # Tenant can access their own payments
        if obj.lease.tenant and obj.lease.tenant.id == request.user.id:
            return True
        return False


class IsMaintenanceRelatedParty(permissions.BasePermission):
    """Allow parties related to maintenance request"""

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True
        # Property owner can access maintenance for their properties
        if obj.property.owner == request.user:
            return True
        # Tenant can access maintenance requests they submitted
        if obj.tenant and obj.tenant.id == request.user.id:
            return True
        # Assigned staff can access
        if obj.assigned_to == request.user:
            return True
        return False
